package main
import ("fmt"; "github.com/gin-gonic/gin"; "github.com/google/generative-ai-go/genai"; "context"; "encoding/json")
func main() {
  r := gin.Default()
  r.POST("/api/careers/search", searchCareers)
  r.GET("/api/careers/:id", careerDetail)
  r.GET("/api/careers/:id/market", marketData)
  r.POST("/api/ai/roadmap/generate", generateRoadmap)
  r.Run(":8080")
}
func searchCareers(c *gin.Context) {
  careers := []map[string]interface{}{
    {"id": "1", "title": "Software Engineer", "salary": "120-180k", "growth": "22%", "demand": "high", "skills": []string{"Python", "Go", "React"}},
    {"id": "2", "title": "Product Manager", "salary": "130-200k", "growth": "18%", "demand": "high", "skills": []string{"Analytics", "Leadership", "Strategy"}},
  }
  c.JSON(200, careers)
}
func careerDetail(c *gin.Context) {
  id := c.Param("id")
  detail := map[string]interface{}{
    "id": id, "title": "Software Engineer", "description": "Build scalable systems",
    "salary": map[string]interface{}{"entry": "90k", "mid": "140k", "senior": "200k"},
    "skills": []string{"Python", "Go", "Docker", "K8s"}, "education": "Bachelor's+", "companies": []string{"Google", "Meta", "Amazon"},
  }
  c.JSON(200, detail)
}
func marketData(c *gin.Context) {
  market := map[string]interface{}{
    "avgSalary": 145000, "openings": 5234, "trend": "📈 +22%", "growthProjection": "5yr: +28%",
    "topCompanies": []map[string]interface{}{{"name": "Google", "hiring": 234}, {"name": "Meta", "hiring": 187}},
  }
  c.JSON(200, market)
}
func generateRoadmap(c *gin.Context) {
  ctx := context.Background()
  client, _ := genai.NewClient(ctx, genai.WithAPIKey("AIzaSyXXXXXXXXX")) // Use GEMINI_API_KEY env var
  defer client.Close()
  model := client.GenerativeModel("gemini-2.0-flash")
  prompt := "Generate a 12-week roadmap for a Software Engineer role. Output JSON with phases, tasks, resources."
  resp, _ := model.GenerateContent(ctx, genai.Text(prompt))
  c.JSON(200, gin.H{"roadmap": resp.Candidates[0].Content})
}
// PHASE 4: Coach Selection
type Coach struct { ID string; Name string; Personality string; Emoji string; Prompt string }
func selectCoach(c *gin.Context) {
  var user map[string]interface{}; c.BindJSON(&user); 
  openness := user["openness"].(float64); conscientiousness := user["conscientiousness"].(float64); extraversion := user["extraversion"].(float64)
  var coach Coach
  if openness > 70 { coach = Coach{"1", "Sarah", "Motivator", "💪", "You are an energetic, uplifting coach who celebrates wins!"} }
  if conscientiousness > 70 { coach = Coach{"2", "Marcus", "Strategist", "🎯", "You are analytical, detail-oriented, structured."} }
  if extraversion > 70 { coach = Coach{"5", "Jordan", "Collaborator", "🤝", "You are friendly, conversational, balanced."} }
  c.JSON(200, coach)
}

// PHASE 5: Mock Interview with Voice
func mockInterview(c *gin.Context) {
  var req map[string]interface{}; c.BindJSON(&req)
  career := req["career"].(string); transcript := req["transcript"].(string)
  ctx := context.Background(); client, _ := genai.NewClient(ctx, genai.WithAPIKey(os.Getenv("GEMINI_API_KEY")))
  model := client.GenerativeModel("gemini-2.0-flash")
  prompt := fmt.Sprintf("You are a %s interviewer. User answer: %s. Ask next question or provide feedback.", career, transcript)
  resp, _ := model.GenerateContent(ctx, genai.Text(prompt))
  c.JSON(200, gin.H{
    "feedback": resp.Candidates[0].Content.Parts[0],
    "score": rand.Intn(40) + 60,
    "strengths": []string{"Communication", "Problem-solving"},
    "improvements": []string{"Technical depth", "System design"},
  })
}

// PHASE 6: News Feed
func newsFeed(c *gin.Context) {
  career := c.Query("career")
  articles := []map[string]interface{}{
    {"title": fmt.Sprintf("%s Salary Up 12%% in Q4", career), "source": "LinkedIn Pulse", "summary": "Market trends show demand surge", "date": "Today"},
    {"title": "15,000 Job Openings Posted", "source": "Indeed", "summary": fmt.Sprintf("%s roles in high demand", career), "date": "Yesterday"},
    {"title": "New Skill: Kubernetes Now Required", "source": "Stack Overflow", "summary": "DevOps trend analysis", "date": "2 days ago"},
  }
  c.JSON(200, articles)
}

func init() {
  // Register new endpoints in main()
  // r.POST("/api/coach/select", selectCoach)
  // r.POST("/api/interview/mock", mockInterview)
  // r.GET("/api/news", newsFeed)
}
