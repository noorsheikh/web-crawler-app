import React, { useState, useEffect, useRef } from "react";
import { CrawlStats } from "./types";
import HeaderHero from "./components/HeaderHero";
import SearchBar from "./components/SearchBar";
import ResultsTable from "./components/ResultsTable";
import CrawlStatsCards from "./components/CrawlStatsCards";
import StatusCodesStats from "./components/StatusCodesStats";
import PerDomainUrlStats from "./components/PerDomainUrlStats";

const LandingPage: React.FC = () => {
  const [stats, setStats] = useState<CrawlStats | undefined>();

  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    setupCrawlWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const setupCrawlWebSocket = async () => {
    try {
      if (wsRef.current) {
        wsRef.current.close();
      }

      wsRef.current = new WebSocket("ws://localhost:8000/ws/crawl/");
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const stats: CrawlStats = {
          urls: data?.total_urls,
          errors: data?.errors,
          statusCount: Object.keys(data?.status_counts || {}).map(
            (statusNumber) => ({
              code: statusNumber,
              total: data?.status_counts[statusNumber],
            })
          ),
          domainsCount: Object.keys(data?.domain_counts || {}).map(
            (domain) => ({
              domain,
              total: data?.domain_counts[domain],
            })
          ),
          records: data?.results,
        };
        setStats(stats);
      };
    } catch (err) {
      console.error("Failed to start crawl:", err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 py-10 px-4 pt-5">
      <div className="w-9 mx-auto text-center space-y-8">
        <HeaderHero />
        <SearchBar />
      </div>

      <div className="grid w-9 mx-auto text-center">
        <div className="col-8">
          <div className="grid">
            <CrawlStatsCards
              urls={stats?.urls || 0}
              errors={stats?.errors || 0}
            />
            <div className="col-12">
              <ResultsTable data={stats?.records || []} />
            </div>
          </div>
        </div>
        <div className="col-4">
          <div className="grid">
            <div className="col-12">
              {stats?.statusCount && (
                <StatusCodesStats statusCount={stats?.statusCount} />
              )}
            </div>
            <div className="col-12">
              {stats?.domainsCount && (
                <PerDomainUrlStats domainsCount={stats?.domainsCount} />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
