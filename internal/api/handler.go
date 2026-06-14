package api

import (
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/oklog/ulid/v2"

	"github.com/silvertiger/autoingest/internal/llm"
	"github.com/silvertiger/autoingest/internal/parser"
	"github.com/silvertiger/autoingest/internal/store"
)

type AppConfig struct {
	Port        int
	DBPath      string
	UploadDir   string
	LLMBaseURL  string
	LLMModel    string
	LLMTimeout  time.Duration
	MaxFileSize int
}

type Handler struct {
	cfg      *AppConfig
	db       *store.SQLiteStore
	registry *parser.Registry
	llmCl    *llm.Client
	tmpls    *template.Template
}

func New(cfg *AppConfig, db *store.SQLiteStore, tmplDir string) (*Handler, error) {
	funcs := template.FuncMap{
		"formatTime": func(t time.Time) string { return t.Format("15:04") },
		"pct":        func(f float64) string { return fmt.Sprintf("%.0f%%", f*100) },
		"ago": func(t time.Time) string {
			d := time.Since(t)
			if d < time.Minute { return "just now" }
			if d < time.Hour { return fmt.Sprintf("%dm ago", int(d.Minutes())) }
			if d < 24*time.Hour { return fmt.Sprintf("%dh ago", int(d.Hours())) }
			return t.Format("Jan 2")
		},
		"add": func(a, b int) int { return a + b },
		"sub": func(a, b int) int { return a - b },
	}
	base := template.New("base").Funcs(funcs)
	tmpls, err := base.ParseGlob(filepath.Join(tmplDir, "*.html"))
	if err != nil {
		return nil, fmt.Errorf("parse templates: %w", err)
	}
	return &Handler{
		cfg:      cfg,
		db:       db,
		registry: parser.NewRegistry(),
		llmCl:    llm.New(cfg.LLMBaseURL, cfg.LLMModel, cfg.LLMTimeout),
		tmpls:    tmpls,
	}, nil
}

func (h *Handler) Router() *chi.Mux {
	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.RequestID)
	r.Handle("/static/*", http.FileServer(http.Dir("static")))
	r.Get("/", h.pageInput)
	r.Get("/input", h.pageInput)
	r.Get("/history", h.pageHistory)
	r.Get("/result/{id}", h.pageResult)
	r.Post("/api/ingest", h.apiIngest)
	r.Get("/api/jobs/{id}", h.apiGetJob)
	r.Get("/api/results", h.apiListResults)
	r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
		json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	})
	return r
}

func (h *Handler) pageInput(w http.ResponseWriter, r *http.Request) {
	h.tmpls.ExecuteTemplate(w, "input.html", nil)
}

func (h *Handler) pageHistory(w http.ResponseWriter, r *http.Request) {
	limitStr := r.URL.Query().Get("limit")
	limit, _ := strconv.Atoi(limitStr)
	if limit <= 0 { limit = 50 }
	offsetStr := r.URL.Query().Get("offset")
	offset, _ := strconv.Atoi(offsetStr)

	records, err := h.db.List(limit, offset)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	total, _ := h.db.Count()
	if err := h.tmpls.ExecuteTemplate(w, "history.html", map[string]interface{}{
		"Records": records, "Total": total, "Limit": limit, "Offset": offset,
	}); err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
}

func (h *Handler) pageResult(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	rec, err := h.db.Get(id)
	if err != nil {
		http.Error(w, "not found", 404)
		return
	}
	if err := h.tmpls.ExecuteTemplate(w, "result.html", rec); err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
}

func (h *Handler) apiIngest(w http.ResponseWriter, r *http.Request) {
	maxSize := int64(h.cfg.MaxFileSize) * 1024 * 1024
	r.Body = http.MaxBytesReader(w, r.Body, maxSize)

	file, header, err := r.FormFile("file")
	if err != nil {
		jsonErr(w, 400, "missing or invalid file field")
		return
	}
	defer file.Close()

	ext := strings.ToLower(filepath.Ext(header.Filename))
	if !h.canHandle(ext) {
		jsonErr(w, 400, "unsupported file type: "+ext)
		return
	}

	tmpPath, err := h.saveTemp(file, header.Filename)
	if err != nil {
		jsonErr(w, 500, "save file: "+err.Error())
		return
	}
	defer os.Remove(tmpPath)

	jobID := ulid.Make().String()
	h.db.Insert(&store.HistoryRecord{
		ID: jobID, FileName: header.Filename, FileType: strings.TrimPrefix(ext, "."),
		FileSize: header.Size, FilePath: tmpPath,
	})
	h.db.UpdateStatus(jobID, "parsing", "")

	parseResult, pErr := h.registry.Parse(tmpPath)
	if pErr != nil {
		h.db.UpdateComplete(jobID, "unknown", "", "", 0, pErr.Error())
		jsonErr(w, 422, "parse failed: "+pErr.Error())
		return
	}

	cls, cErr := h.llmCl.Classify(r.Context(), parseResult.Text, h.schemaSummary())
	if cErr != nil {
		efB, _ := json.Marshal(parseResult.Metadata)
		h.db.UpdateComplete(jobID, "raw", parseResult.Text[:min(len(parseResult.Text),500)], string(efB), 1.0, "classify failed: "+cErr.Error())
		jsonOK(w, map[string]any{"job_id": jobID, "status": "completed", "metric_type": "raw", "confidence": 0, "error": cErr.Error()})
		return
	}
	efB, _ := json.Marshal(cls.ExtractedFields)
	h.db.UpdateComplete(jobID, cls.MetricType, cls.Reasoning, string(efB), cls.Confidence, "")
	jsonOK(w, map[string]any{
		"job_id": jobID, "status": "completed",
		"metric_type": cls.MetricType, "confidence": cls.Confidence,
		"url": "/result/" + jobID,
	})
}

func (h *Handler) apiGetJob(w http.ResponseWriter, r *http.Request) {
	rec, err := h.db.Get(chi.URLParam(r, "id"))
	if err != nil { jsonErr(w, 404, "not found"); return }
	jsonOK(w, rec)
}

func (h *Handler) apiListResults(w http.ResponseWriter, r *http.Request) {
	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	if limit <= 0 { limit = 50 }
	offset, _ := strconv.Atoi(r.URL.Query().Get("offset"))
	recs, err := h.db.List(limit, offset)
	if err != nil { jsonErr(w, 500, err.Error()); return }
	jsonOK(w, map[string]any{"results": recs, "count": len(recs)})
}

func (h *Handler) canHandle(ext string) bool {
	_, err := h.registry.Parse("fake" + ext)
	return err == nil || !strings.HasPrefix(err.Error(), "no parser")
}

func (h *Handler) saveTemp(reader multipart.File, fname string) (string, error) {
	dir := h.cfg.UploadDir
	os.MkdirAll(dir, 0o755)
	ext := filepath.Ext(fname)
	tmp, err := os.CreateTemp(dir, "ai-*"+ext)
	if err != nil { return "", err }
	defer tmp.Close()
	if _, err := io.Copy(tmp, reader); err != nil {
		os.Remove(tmp.Name())
		return "", err
	}
	return tmp.Name(), nil
}

func (h *Handler) schemaSummary() string {
	return "revenue, kpi_performance, inventory, employee_data, financial_statement"
}

func jsonOK(w http.ResponseWriter, v any) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(v)
}

func jsonErr(w http.ResponseWriter, code int, msg string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(map[string]string{"error": msg})
}

func min(a, b int) int { if a < b { return a }; return b }
