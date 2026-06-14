package parser

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/xuri/excelize/v2"
)

type ParseResult struct {
	Text     string         `json:"text"`
	Metadata map[string]any `json:"metadata"`
}

type Parser interface {
	Parse(filePath string) (*ParseResult, error)
	SupportedExtensions() []string
}

type Registry struct {
	parsers map[string]Parser
}

func NewRegistry() *Registry {
	r := &Registry{parsers: make(map[string]Parser)}
	r.Register(TextParser{})
	r.Register(CSVParser{})
	r.Register(HTMLParser{})
	r.Register(ExcelParser{})
	r.Register(PDFParserStub{})
	return r
}

func (r *Registry) Register(p Parser) {
	for _, ext := range p.SupportedExtensions() {
		r.parsers[strings.ToLower(ext)] = p
	}
}

func (r *Registry) Supports(ext string) bool {
	_, ok := r.parsers[strings.ToLower(ext)]
	return ok
}

func (r *Registry) Parse(filePath string) (*ParseResult, error) {
	ext := strings.ToLower(filepath.Ext(filePath))
	p, ok := r.parsers[ext]
	if !ok {
		return nil, fmt.Errorf("no parser for extension: %s", ext)
	}
	return p.Parse(filePath)
}

// ── Text ─────────────────────────────────────────────────────

type TextParser struct{}

func (TextParser) SupportedExtensions() []string { return []string{".txt", ".md"} }

func (TextParser) Parse(fp string) (*ParseResult, error) {
	data, err := os.ReadFile(fp)
	if err != nil {
		return nil, err
	}
	return &ParseResult{
		Text:     string(data),
		Metadata: map[string]any{"format": "text"},
	}, nil
}

// ── CSV ──────────────────────────────────────────────────────

type CSVParser struct{}

func (CSVParser) SupportedExtensions() []string { return []string{".csv"} }

func (CSVParser) Parse(fp string) (*ParseResult, error) {
	data, err := os.ReadFile(fp)
	if err != nil {
		return nil, err
	}
	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	if len(lines) == 0 {
		return &ParseResult{Text: "", Metadata: map[string]any{"format": "csv", "rows": 0}}, nil
	}
	var sb strings.Builder
	sb.WriteString("Columns: " + lines[0] + "\n")
	for i := 1; i < len(lines); i++ {
		sb.WriteString(fmt.Sprintf("Row %d: %s\n", i, lines[i]))
	}
	return &ParseResult{
		Text:     sb.String(),
		Metadata: map[string]any{"format": "csv", "rows": len(lines) - 1},
	}, nil
}

// ── HTML ─────────────────────────────────────────────────────

type HTMLParser struct{}

func (HTMLParser) SupportedExtensions() []string { return []string{".html", ".htm"} }

func (HTMLParser) Parse(fp string) (*ParseResult, error) {
	data, err := os.ReadFile(fp)
	if err != nil {
		return nil, err
	}
	return &ParseResult{
		Text:     stripHTMLTags(string(data)),
		Metadata: map[string]any{"format": "html"},
	}, nil
}

func stripHTMLTags(html string) string {
	html = stripTag(html, "script")
	html = stripTag(html, "style")
	result := ""
	inTag := false
	for _, ch := range html {
		if ch == '<' {
			inTag = true
			continue
		}
		if ch == '>' {
			inTag = false
			continue
		}
		if !inTag {
			result += string(ch)
		}
	}
	var out strings.Builder
	lastSpace := true
	for _, ch := range result {
		if ch == ' ' || ch == '\t' || ch == '\n' || ch == '\r' {
			if !lastSpace {
				out.WriteRune(' ')
				lastSpace = true
			}
		} else {
			out.WriteRune(ch)
			lastSpace = false
		}
	}
	return strings.TrimSpace(out.String())
}

func stripTag(html, tag string) string {
	lower := strings.ToLower(html)
	for {
		startTag := "<" + tag
		endTag := "</" + tag + ">"
		si := strings.Index(lower, startTag)
		if si == -1 {
			break
		}
		ei := strings.Index(lower[si:], endTag)
		if ei == -1 {
			break
		}
		ei += si + len(endTag)
		html = html[:si] + html[ei:]
		lower = strings.ToLower(html)
	}
	return html
}

// ── Excel (streaming row iterate) ────────────────────────────

type ExcelParser struct{}

func (ExcelParser) SupportedExtensions() []string { return []string{".xlsx"} }

func (ExcelParser) Parse(fp string) (*ParseResult, error) {
	f, err := excelize.OpenFile(fp)
	if err != nil {
		return nil, fmt.Errorf("excelize open: %w", err)
	}
	defer f.Close()

	sheetNames := f.GetSheetList()
	var sb strings.Builder
	for _, sheetName := range sheetNames {
		rows, err := f.GetRows(sheetName)
		if err != nil {
			continue
		}
		sb.WriteString(fmt.Sprintf("Sheet: %s\n", sheetName))
		for i, row := range rows {
			sb.WriteString(fmt.Sprintf("Row %d: %s\n", i+1, strings.Join(row, " | ")))
		}
	}
	return &ParseResult{
		Text:     sb.String(),
		Metadata: map[string]any{"format": "xlsx", "sheets": len(sheetNames)},
	}, nil
}

// ── PDF (stub — TODO: integrate unipdf or pymupdf sidecar) ─

type PDFParserStub struct{}

func (PDFParserStub) SupportedExtensions() []string { return []string{".pdf"} }

func (PDFParserStub) Parse(fp string) (*ParseResult, error) {
	data, err := os.ReadFile(fp)
	if err != nil {
		return nil, err
	}
	return &ParseResult{
		Text:     fmt.Sprintf("[PDF stub — raw %d bytes — full parser pending]", len(data)),
		Metadata: map[string]any{"format": "pdf", "size_bytes": len(data), "note": "pdf parser not yet integrated"},
	}, nil
}
