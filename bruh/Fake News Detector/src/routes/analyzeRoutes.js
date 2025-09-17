import { Router } from "express";

export function createAnalyzeRouter(controller, upload) {
  const router = Router();
  router.post("/analyze", controller.analyzeText);
  router.post("/analyze-url", controller.analyzeUrl);
  router.post("/analyze-image", upload.single('image'), controller.analyzeImage);
  return router;
}


