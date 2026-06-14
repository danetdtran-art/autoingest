package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/silvertiger/autoingest/internal/api"
	"github.com/silvertiger/autoingest/internal/store"
)

func loadConfig() *api.AppConfig {
	cfg := &api.AppConfig{
		Port:        3080,
		DBPath:      "data/history.db",
		UploadDir:   "data/uploads",
		LLMBaseURL:  "http://localhost:20128/v1",
		LLMModel:    "cx/gpt-5.5",
		LLMTimeout:  120 * time.Second,
		MaxFileSize: 50,
	}
	if p := os.Getenv("AUTOINGEST_PORT"); p != "" { fmt.Sscanf(p, "%d", &cfg.Port) }
	if d := os.Getenv("AUTOINGEST_DB_PATH"); d != "" { cfg.DBPath = d }
	if u := os.Getenv("AUTOINGEST_UPLOAD_DIR"); u != "" { cfg.UploadDir = u }
	if u := os.Getenv("AUTOINGEST_LLM_BASE_URL"); u != "" { cfg.LLMBaseURL = u }
	if u := os.Getenv("AUTOINGEST_LLM_MODEL"); u != "" { cfg.LLMModel = u }
	if u := os.Getenv("AUTOINGEST_MAX_FILE_SIZE_MB"); u != "" { fmt.Sscanf(u, "%d", &cfg.MaxFileSize) }
	os.MkdirAll("data/uploads", 0o755)
	return cfg
}

func main() {
	cfg := loadConfig()
	log.Printf("config: port=%d db=%s upload=%s llm=%s model=%s",
		cfg.Port, cfg.DBPath, cfg.UploadDir, cfg.LLMBaseURL, cfg.LLMModel)

	db, err := store.NewSQLite(cfg.DBPath)
	if err != nil { log.Fatalf("sqlite: %v", err) }
	defer db.Close()

	h, err := api.New(cfg, db, "templates")
	if err != nil { log.Fatalf("api: %v", err) }

	addr := fmt.Sprintf(":%d", cfg.Port)
	log.Printf("listening on %s", addr)

	srv := &http.Server{
		Addr: addr, Handler: h.Router(),
		ReadTimeout: 30 * time.Second, WriteTimeout: 120 * time.Second,
	}
	if err := srv.ListenAndServe(); err != nil {
		log.Fatalf("server: %v", err)
	}
}
