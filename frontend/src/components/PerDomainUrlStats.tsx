import { Card } from "primereact/card";
import { DomainCount } from "../types";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";

type PerDomainUrlStatsProps = {
  domainsCount: DomainCount[];
};

const PerDomainUrlStats = ({ domainsCount }: PerDomainUrlStatsProps) => (
  <Card title="Per Domain URLs Statistics" className="text-left">
    <DataTable
      value={domainsCount}
      emptyMessage="Scan a URL to see the results"
    >
      <Column field="domain" header="Domain" />
      <Column field="total" header="Total" />
    </DataTable>
  </Card>
);

export default PerDomainUrlStats;
