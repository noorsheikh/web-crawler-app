export type CrawlRecord = {
  title: string;
  url: string;
  status: number;
  size: number;
};

export type StatusCount = { code: string; total: number };

export type DomainCount = { domain: string; total: number };

export type CrawlStats = {
  urls: number;
  errors: number;
  statusCount: StatusCount[];
  domainsCount: DomainCount[];
  records: CrawlRecord[];
};

export type CrawlRequest = {
  startUrl: string;
  maxDepth: number;
  allowedDomains: string[];
  blacklistedDomains: string[];
};
