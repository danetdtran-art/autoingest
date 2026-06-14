package store

import (
	"database/sql"
	"fmt"
	"os"
	"path/filepath"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

type HistoryRecord struct {
	ID               string    `json:"id"`
	FileName         string    `json:"file_name"`
	FileType         string    `json:"file_type"`
	FileSize         int64     `json:"file_size"`
	FilePath         string    `json:"file_path"`
	MetricType       string    `json:"metric_type"`
	Confidence       float64   `json:"confidence"`
	Reasoning        string    `json:"reasoning"`
	ExtractedFields  string    `json:"extracted_fields"` // JSON string
	RawText          string    `json:"-"`
	CreatedAt        time.Time `json:"created_at"`
	Status           string    `json:"status"`
	Error            string    `json:"error,omitempty"`
}

type SQLiteStore struct {
	db *sql.DB
}

func NewSQLite(dbPath string) (*SQLiteStore, error) {
	dir := filepath.Dir(dbPath)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return nil, fmt.Errorf("create dir: %w", err)
	}

	db, err := sql.Open("sqlite3", dbPath+"?_journal_mode=WAL&_busy_timeout=5000")
	if err != nil {
		return nil, fmt.Errorf("open sqlite: %w", err)
	}

	s := &SQLiteStore{db: db}
	if err := s.init(); err != nil {
		db.Close()
		return nil, err
	}
	return s, nil
}

func (s *SQLiteStore) init() error {
	query := `
	CREATE TABLE IF NOT EXISTS history (
		id TEXT PRIMARY KEY,
		file_name TEXT NOT NULL,
		file_type TEXT NOT NULL,
		file_size INTEGER NOT NULL,
		file_path TEXT,
		metric_type TEXT NOT NULL,
		confidence REAL NOT NULL,
		reasoning TEXT,
		extracted_fields TEXT,
		raw_text TEXT,
		status TEXT NOT NULL DEFAULT 'queued',
		error TEXT,
		created_at TEXT NOT NULL
	);
	CREATE INDEX IF NOT EXISTS idx_history_created ON history(created_at DESC);
	`
	_, err := s.db.Exec(query)
	return err
}

func (s *SQLiteStore) Insert(rec *HistoryRecord) error {
	rec.CreatedAt = time.Now()
	rec.Status = "queued"
	_, err := s.db.Exec(`
		INSERT INTO history (id, file_name, file_type, file_size, file_path, metric_type, confidence, reasoning, extracted_fields, raw_text, status, error, created_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	`, rec.ID, rec.FileName, rec.FileType, rec.FileSize, rec.FilePath, rec.MetricType, rec.Confidence, rec.Reasoning, rec.ExtractedFields, rec.RawText, rec.Status, rec.Error, rec.CreatedAt.Format(time.RFC3339))
	return err
}

func (s *SQLiteStore) UpdateStatus(id, status, errMsg string) error {
	set := "status = ?, updated_at = ?"
	_, err := s.db.Exec(`UPDATE history SET `+set+` WHERE id = ?`, status, time.Now().Format(time.RFC3339), id)
	return err
}

func (s *SQLiteStore) UpdateComplete(id, metricType, reasoning, extractedFields, rawText string, confidence float64, errMsg string) error {
	_, err := s.db.Exec(`
		UPDATE history SET
			metric_type = ?,
			confidence = ?,
			reasoning = ?,
			extracted_fields = ?,
			raw_text = ?,
			error = ?,
			status = 'completed'
		WHERE id = ?
	`, metricType, confidence, reasoning, extractedFields, rawText, errMsg, id)
	return err
}

func (s *SQLiteStore) Get(id string) (*HistoryRecord, error) {
	var rec HistoryRecord
	var createdAt string
	err := s.db.QueryRow(`
		SELECT id, file_name, file_type, file_size, file_path, metric_type, confidence, reasoning, extracted_fields, raw_text, status, COALESCE(error,''), created_at
		FROM history WHERE id = ?
	`, id).Scan(&rec.ID, &rec.FileName, &rec.FileType, &rec.FileSize, &rec.FilePath, &rec.MetricType, &rec.Confidence, &rec.Reasoning, &rec.ExtractedFields, &rec.RawText, &rec.Status, &rec.Error, &createdAt)
	if err != nil {
		return nil, err
	}
	rec.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)
	return &rec, nil
}

func (s *SQLiteStore) List(limit, offset int) ([]HistoryRecord, error) {
	rows, err := s.db.Query(`
		SELECT id, file_name, file_type, file_size, metric_type, confidence, status, COALESCE(error,''), created_at
		FROM history ORDER BY created_at DESC LIMIT ? OFFSET ?
	`, limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var results []HistoryRecord
	for rows.Next() {
		var rec HistoryRecord
		var createdAt string
		if err := rows.Scan(&rec.ID, &rec.FileName, &rec.FileType, &rec.FileSize, &rec.MetricType, &rec.Confidence, &rec.Status, &rec.Error, &createdAt); err != nil {
			return nil, err
		}
		rec.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)
		results = append(results, rec)
	}
	return results, rows.Err()
}

func (s *SQLiteStore) Count() (int, error) {
	var n int
	err := s.db.QueryRow("SELECT COUNT(*) FROM history").Scan(&n)
	return n, err
}

func (s *SQLiteStore) Close() error {
	return s.db.Close()
}
