package llm

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/kaptinlin/jsonrepair"
	"github.com/openai/openai-go"
	"github.com/openai/openai-go/option"
	"github.com/openai/openai-go/shared"
)

type Client struct {
	cfg     openai.ChatCompletionNewParams
	client  openai.Client
}

func New(baseURL, model string, timeout time.Duration) *Client {
	opts := []option.RequestOption{option.WithMaxRetries(2)}
	if baseURL != "" {
		opts = append(opts, option.WithBaseURL(baseURL))
	}
	return &Client{
		cfg: openai.ChatCompletionNewParams{
			Model:       shared.ChatModel(model),
			Temperature: openai.Float(0.0),
		},
		client: openai.NewClient(opts...),
	}
}

type ClassificationResponse struct {
	MetricType      string         `json:"metric_type"`
	ExtractedFields map[string]any `json:"extracted_fields"`
	Confidence      float64        `json:"confidence"`
	Reasoning       string         `json:"reasoning"`
}

func (c *Client) Classify(ctx context.Context, text string, schemasSummary string) (*ClassificationResponse, error) {
	systemPrompt := `You are a data classification and extraction assistant.
Read the document text and determine which metric schema it matches from the list below.
Return ONLY valid JSON with keys: metric_type, extracted_fields, confidence (0-1), reasoning.

Available schemas:
` + schemasSummary + `

If no schema matches, return:
{"metric_type":"unknown","extracted_fields":{},"confidence":0.0,"reasoning":"no schema matched"}

IMPORTANT: Return ONLY valid JSON. No markdown blocks, no extra text.`

	userPrompt := fmt.Sprintf("## Document Text\n\n%s", truncate(text, 80000))

	params := c.cfg
	params.Messages = []openai.ChatCompletionMessageParamUnion{
		openai.SystemMessage(systemPrompt),
		openai.UserMessage(userPrompt),
	}

	ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
	defer cancel()

	chat, err := c.client.Chat.Completions.New(ctx, params)
	if err != nil {
		return nil, fmt.Errorf("llm chat: %w", err)
	}
	if len(chat.Choices) == 0 {
		return nil, fmt.Errorf("llm returned empty choices")
	}

	raw := chat.Choices[0].Message.Content
	return parseResponse(raw)
}

func parseResponse(raw string) (*ClassificationResponse, error) {
	var result ClassificationResponse
	if err := json.Unmarshal([]byte(raw), &result); err == nil {
		return &result, nil
	}
	repaired, err := jsonrepair.Repair(raw)
	if err != nil {
		return nil, fmt.Errorf("json repair failed: %w", err)
	}
	if err := json.Unmarshal([]byte(repaired), &result); err != nil {
		return nil, fmt.Errorf("json unmarshal after repair: %w", err)
	}
	return &result, nil
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n] + "\n...[truncated]"
}
