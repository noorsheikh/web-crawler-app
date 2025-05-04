import { Card } from "primereact/card";
import { Column } from "primereact/column";
import { DataTable } from "primereact/datatable";
import { StatusCount } from "../types";

type StatusCodesStatsProps = {
  statusCount: StatusCount[];
};

const StatusCodesStats = ({ statusCount }: StatusCodesStatsProps) => (
  <Card title="Status Code Statistics" className="text-left">
    <DataTable value={statusCount} emptyMessage="Scan a URL to see the results">
      <Column field="code" header="Code" />
      <Column field="total" header="Total" />
    </DataTable>
  </Card>
);

export default StatusCodesStats;
