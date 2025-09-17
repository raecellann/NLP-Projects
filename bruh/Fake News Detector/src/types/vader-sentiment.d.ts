/// <reference types="node" />
declare module "vader-sentiment" {
  export namespace SentimentIntensityAnalyzer {
    function polarity_scores(text: string): {
      compound: number;
      neg: number;
      neu: number;
      pos: number;
    };
  }
  const _default: { SentimentIntensityAnalyzer: typeof SentimentIntensityAnalyzer };
  export default _default;
}


