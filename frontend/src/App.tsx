import React, { useState, useEffect, useRef } from "react";
import { Card } from "primereact/card";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { CrawlStats } from "./types";
import HeaderHero from "./components/HeaderHero";
import SearchBar from "./components/SearchBar";
import ResultsTable from "./components/ResultsTable";

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
            <div className="col-6">
              <Card title="Scanned URLs" className="text-left">
                <p className="text-5xl font-semibold m-0">{stats?.urls}</p>
              </Card>
            </div>
            <div className="col-6">
              <Card title="Errors" className="text-left">
                <p className="text-5xl font-semibold m-0">{stats?.errors}</p>
              </Card>
            </div>
            <div className="col-12">
              <ResultsTable data={stats?.records || []} />
            </div>
          </div>
        </div>
        <div className="col-4">
          <div className="grid">
            <div className="col-12">
              <Card title="Status Code Statistics" className="text-left">
                <DataTable
                  value={stats?.statusCount}
                  emptyMessage="Scan a URL to see the results"
                >
                  <Column field="code" header="Code" />
                  <Column field="total" header="Total" />
                </DataTable>
              </Card>
            </div>
            <div className="col-12">
              <Card title="Per Domain URLs Statistics" className="text-left">
                <DataTable
                  value={stats?.domainsCount}
                  emptyMessage="Scan a URL to see the results"
                >
                  <Column field="domain" header="Domain" />
                  <Column field="total" header="Total" />
                </DataTable>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
