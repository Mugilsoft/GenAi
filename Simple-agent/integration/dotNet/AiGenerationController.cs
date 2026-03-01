using Microsoft.AspNetCore.Mvc;
using System.Text.Json.Serialization;

namespace SimpleCodingAgent.Integrations.DotNet
{
    [ApiController]
    [Route("api/[controller]")]
    public class AiGenerationController : ControllerBase
    {
        private readonly HttpClient _httpClient;
        private const string PythonApiUrl = "http://localhost:5000/generate";

        public AiGenerationController(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        [HttpPost("generate")]
        public async Task<IActionResult> Generate([FromBody] GenerationRequest request)
        {
            try
            {
                // Proxy the request to the Python Flask API
                var response = await _httpClient.PostAsJsonAsync(PythonApiUrl, request);
                
                if (!response.IsSuccessStatusCode)
                {
                    var error = await response.Content.ReadAsStringAsync();
                    return StatusCode((int)response.StatusCode, error);
                }

                var result = await response.Content.ReadFromJsonAsync<GenerationResponse>();
                return Ok(result);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }

    public class GenerationRequest
    {
        [JsonPropertyName("language")]
        public string Language { get; set; } = string.Empty;

        [JsonPropertyName("framework")]
        public string Framework { get; set; } = string.Empty;

        [JsonPropertyName("task")]
        public string Task { get; set; } = string.Empty;

        [JsonPropertyName("context")]
        public string? Context { get; set; }

        [JsonPropertyName("temperature")]
        public float? Temperature { get; set; }
    }

    public class GenerationResponse
    {
        [JsonPropertyName("code")]
        public string Code { get; set; } = string.Empty;

        [JsonPropertyName("language")]
        public string Language { get; set; } = string.Empty;

        [JsonPropertyName("framework")]
        public string Framework { get; set; } = string.Empty;

        [JsonPropertyName("task")]
        public string Task { get; set; } = string.Empty;

        [JsonPropertyName("timestamp")]
        public string Timestamp { get; set; } = string.Empty;
    }
}
