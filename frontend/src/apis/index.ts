import axios from "axios";
import qs from "qs";
import { CrawlRequest } from "../types";

const BACKEND_URL_BASE = "http://0.0.0.0:8000";

export const startCrawling = async ({
  startUrl,
  maxDepth,
  allowedDomains,
  blacklistedDomains,
}: CrawlRequest) => {
  try {
    const data = qs.stringify({
      url: startUrl,
      max_depth: maxDepth,
      domains: allowedDomains,
      blacklisted: blacklistedDomains,
    });

    await axios.post(`${BACKEND_URL_BASE}/api/crawler/start/`, data, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      maxBodyLength: Infinity,
    });
  } catch (error) {
    console.error("Error starting crawl:", error);
  }
};
