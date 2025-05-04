export type CrawlRecord = {
  title: string;
  url: string;
  status: number;
  size: number;
};

export type CrawlStats = {
  urls: number;
  errors: number;
  statusCount: { code: string; total: number }[];
  domainsCount: { domain: string; total: number }[];
  records: CrawlRecord[];
};

export type CrawlRequest = {
  startUrl: string;
  maxDepth: number;
  allowedDomains: string[];
  blacklistedDomains: string[];
};
