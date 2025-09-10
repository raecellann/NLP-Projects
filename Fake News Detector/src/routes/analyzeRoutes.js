import { Router } from "express";

export function createAnalyzeRouter(controller) {
  const router = Router();
  router.post("/analyze", controller.analyzeText);
  router.post("/analyze-url", controller.analyzeUrl);
  return router;
}


