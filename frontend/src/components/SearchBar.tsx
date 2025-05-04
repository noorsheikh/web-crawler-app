import { Button } from "primereact/button";
import { Chips } from "primereact/chips";
import { FloatLabel } from "primereact/floatlabel";
import { IconField } from "primereact/iconfield";
import { InputIcon } from "primereact/inputicon";
import { InputText } from "primereact/inputtext";
import { useState } from "react";
import { startCrawling } from "../apis";

const SearchBar = () => {
  const [startUrl, setStartUrl] = useState<string>("");
  const [maxDepth, setMaxDepth] = useState<number>(2);
  const [allowedDomains, setAllowedDomains] = useState<string[]>([
    "example.com",
  ]);
  const [blacklistedDomains, setBlacklistedDomains] = useState<string[]>([
    ".js",
    ".css",
  ]);

  const startCrawl = async () => {
    try {
      const crawlingRequest = {
        startUrl,
        maxDepth,
        allowedDomains,
        blacklistedDomains,
      };
      await startCrawling(crawlingRequest);
    } catch (error) {
      console.error("Error starting crawler: ", error);
    }
  };

  return (
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
            icon={<i className="pi pi-search text-white" />}
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
  );
};

export default SearchBar;
