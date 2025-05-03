import React, { useState, useEffect, useRef } from "react";
import { InputText } from "primereact/inputtext";
import { IconField } from "primereact/iconfield";
import { InputIcon } from "primereact/inputicon";
import { Chips } from "primereact/chips";
import { Button } from "primereact/button";
import { Card } from "primereact/card";
import { FloatLabel } from "primereact/floatlabel";
import axios from "axios";
import qs from "qs";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";

type CrawlRecord = {
  totalPages: number;
  totalErrors: number;
  totalSize: number;
  avgResponseTime: number;
};

type CrawlStats = {
  urls: number;
  errors: number;
  statusCount: { code: string; total: number }[];
  domainsCount: { domain: string; total: number }[];
};

const LandingPage: React.FC = () => {
  const [startUrl, setStartUrl] = useState<string>("");
  const [maxDepth, setMaxDepth] = useState<number>(2);
  const [allowedDomains, setAllowedDomains] = useState<string[]>([
    "example.com",
  ]);
  const [blacklistedDomains, setBlacklistedDomains] = useState<string[]>([
    ".js",
    ".css",
  ]);
  const [records, setRecords] = useState<CrawlRecord[]>([]);
  const [stats, setStats] = useState<CrawlStats>({
    totalPages: 0,
    totalErrors: 0,
    totalSize: 0,
    avgResponseTime: 0,
  });

  const wsRef = useRef<WebSocket | null>(null);

  const startCrawling = async () => {
    try {
      const data = qs.stringify({
        url: startUrl,
        max_depth: maxDepth,
        domains: allowedDomains,
        blacklisted: blacklistedDomains,
      });

      const response = await axios.post(
        "http://0.0.0.0:8000/api/crawler/start/",
        data,
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          maxBodyLength: Infinity,
        }
      );

      console.log(response.data);
    } catch (error) {
      console.error("Error starting crawl:", error);
    }
  };

  const startCrawl = async () => {
    try {
      await startCrawling();

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
        };
        setStats(stats);
        // if (data.type === "record") {
        //   setRecords((prev) => [...prev, data.record]);
        // } else if (data.type === "stats") {
        // }
      };
    } catch (err) {
      console.error("Failed to start crawl:", err);
    }
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 py-10 px-4 pt-5">
      <div className="w-9 mx-auto text-center space-y-8">
        <div className="block align-items-center justify-content-center">
          <h1 className="text-900 font-bold text-5xl pb-3 text-red-800">
            Smart Web Crawler
          </h1>
          <p className="text-700 text-2xl pb-5 text-gray-300">
            Crawl a website with advanced depth control and domain filtering in
            real time.
          </p>
        </div>

        <div className="flex flex-column p-2">
          <div className="flex flex-row">
            <div className="flex-grow-1">
              <FloatLabel>
                <IconField iconPosition="left">
                  <InputIcon className="pi pi-search pl-1" />
                  <InputText
                    id="search"
                    value={startUrl}
                    onChange={(e) => setStartUrl(e.target.value)}
                    placeholder="Enter URL to Crawl..."
                    className="w-full border-round-3xl border-noround-right border-1 h-3rem border-gray-700"
                  />
                </IconField>
                <label htmlFor="search" className="flex-3 pl-5">
                  Enter URL to Crawl
                </label>
              </FloatLabel>
            </div>

            <div className="flex-none">
              <FloatLabel>
                <InputText
                  id="depth"
                  type="number"
                  value={maxDepth.toString()}
                  onChange={(e) => setMaxDepth(Number(e.target.value))}
                  className="w-full border-noround border-x-none border-1 h-3rem border-gray-700"
                />
                <label htmlFor="depth" className="flex-3">
                  Max Depth
                </label>
              </FloatLabel>
            </div>
            <div className="flex-none">
              <Button
                icon={<i className="pi pi-search" />}
                className="border-round-3xl border-noround-left border-left-none border-1 h-3rem bg-red-800 border-gray-700"
                onClick={startCrawl}
              />
            </div>
          </div>

          <div className="flex flex-row py-5 gap-2">
            <div className="flex flex-column w-full">
              <FloatLabel>
                <Chips
                  id="allowed-domains"
                  value={allowedDomains}
                  onChange={(e) => setAllowedDomains(e.value || [])}
                  separator=","
                  placeholder="Type domain name here and press enter"
                  className="w-full"
                />
                <label htmlFor="allowed-domains" className="flex-3">
                  Allowed Domains
                </label>
              </FloatLabel>
            </div>

            <div className="flex flex-column w-full">
              <FloatLabel>
                <Chips
                  id="blacklisted-domains"
                  value={blacklistedDomains}
                  onChange={(e) => setBlacklistedDomains(e.value || [])}
                  separator=","
                  placeholder="Type blacklisted domain or extension here and press enter"
                  className="w-full"
                />
                <label htmlFor="blacklisted-domains" className="flex-3">
                  Blacklisted Domains
                </label>
              </FloatLabel>
            </div>
          </div>
        </div>
      </div>

      <div className="grid w-9 mx-auto text-center">
        <div className="col-8">
          <div className="grid">
            <div className="col-6">
              <Card title="Scanned URLs" className="text-center">
                <p className="text-2xl font-semibold">{stats.urls}</p>
              </Card>
            </div>
            <div className="col-6">
              <Card title="Errors" className="text-center">
                <p className="text-2xl font-semibold">{stats.errors}</p>
              </Card>
            </div>
          </div>
        </div>
        <div className="col-4">
          <div className="grid">
            <div className="col-12">
              <Card title="Status Code Statistics" className="text-center">
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
              <Card title="Per Domain URLs Statistics" className="text-center">
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

      {/* {records.length > 0 && (
          <div className="bg-white rounded-xl shadow p-4">
            <h3 className="text-xl font-semibold mb-4">Crawl Results</h3>
            <DataTable
              value={records}
              paginator
              rows={10}
              responsiveLayout="scroll"
            >
              <Column
                field="url"
                header="URL"
                style={{ wordBreak: "break-word" }}
              />
              <Column field="status" header="Status" />
              <Column field="response_time_ms" header="Response Time (ms)" />
            </DataTable>
          </div>
        )} */}
    </div>
  );
};

export default LandingPage;
