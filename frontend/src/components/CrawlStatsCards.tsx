import { Card } from "primereact/card";

type CrawlStatsProps = {
  urls: number;
  errors: number;
};

const CrawlStatsCards = ({ urls, errors }: CrawlStatsProps) => (
  <>
    <div className="col-6">
      <Card title="Scanned URLs" className="text-left">
        <p className="text-5xl font-semibold m-0">{urls}</p>
      </Card>
    </div>
    <div className="col-6">
      <Card title="Errors" className="text-left">
        <p className="text-5xl font-semibold m-0">{errors}</p>
      </Card>
    </div>
  </>
);

export default CrawlStatsCards;
