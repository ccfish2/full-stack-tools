import express, { Express, Request, Response } from "express";
import axios from "axios";
import path from "path";

const app: Express = express();
const PORT: number = 9090;

// Middleware
app.use(express.json());
app.use(express.static("public"));

// Get Django API URL from environment or use default
const DJANGO_API_URL: string = process.env.DJANGO_API_URL || "http://localhost:8000";

// Serve the frontend HTML
app.get("/", (req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, "../public/index.html"));
});

// GET /api/data - Retrieve statsig application data
app.get("/api/data", async (req: Request, res: Response) => {
  try {
    // In a real app, you might fetch from a database or call the Django API
    res.json({
      status: "success",
      data: {
        message: "Frontend is connected to the backend",
        timestamp: new Date().toISOString(),
      },
    });
  } catch (error) {
    res.status(500).json({
      status: "error",
      message: String(error),
    });
  }
});

// POST /api/submit - Submit data to Django backend
app.post("/api/submit", async (req: Request, res: Response) => {
  try {
    const { key, key2 } = req.body;

    // Validate input
    if (!key || !key2) {
      res.status(400).json({
        status: "error",
        message: "Missing required fields: key and key2",
      });
      return;
    }

    // Send to Django backend
    const response = await axios.post(
      `${DJANGO_API_URL}/statsig/application/`,
      {
        key,
        key2,
      }
    );

    res.json({
      status: "success",
      message: "Data submitted successfully",
      data: response.data,
    });
  } catch (error) {
    console.error("Error submitting data:", error);
    res.status(500).json({
      status: "error",
      message: String(error),
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Frontend server is running at http://localhost:${PORT}`);
  console.log(`Django API connected to: ${DJANGO_API_URL}`);
});
