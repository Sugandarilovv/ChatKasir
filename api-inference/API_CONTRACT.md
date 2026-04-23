# API Contract – AI2 API ↔ FS-2

> **Version**: 1.0.0  
> **Base URL**: `https://<host>/`  
> **Authentication**: `X-API-Key` header (required on all non-health endpoints)

---

## Authentication

All endpoints except `GET /health` require an API key in the request header:

```
X-API-Key: <your-api-key>
```

Requests with a missing or invalid key receive **HTTP 401**.

---

## Endpoints

### `GET /health`

Returns API and model status. No authentication required.

**Response `200 OK`**
```json
{
  "status": "ok",
  "model_loaded": true,
  "version": "1.0.0"
}
```

| Field | Type | Description |
|---|---|---|
| `status` | `string` | `"ok"` if model is loaded, `"degraded"` otherwise |
| `model_loaded` | `boolean` | Whether the Keras model is in memory |
| `version` | `string` | API version string |

---

### `POST /predict`

Run inference on one or more input samples.

**Request body** (`application/json`)
```json
{
  "inputs": [
    [0.1, 0.2, 0.3, 0.4]
  ]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `inputs` | `array[array[float]]` | ✅ | Batch of input vectors. Each inner array is one sample. |

**Response `200 OK`**
```json
{
  "predictions": [0]
}
```

| Field | Type | Description |
|---|---|---|
| `predictions` | `array` | Model output per sample (class index for classification; raw float for regression) |

---

## Error Responses

All errors follow this schema:

```json
{
  "error": true,
  "error_code": 1001,
  "message": "Human-readable description"
}
```

| HTTP Status | `error_code` | Meaning |
|---|---|---|
| 401 | 4010 | Missing or invalid API key |
| 422 | 1001 | Invalid / malformed input payload |
| 503 | 1002 | Model not loaded |
| 500 | 1003 | Inference failure |
| 500 | 1000 | Unexpected server error |
