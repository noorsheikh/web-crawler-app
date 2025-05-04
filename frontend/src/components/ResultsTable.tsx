import { Column } from "primereact/column";
import { DataTable } from "primereact/datatable";
import { CrawlRecord } from "../types";

type ResultsTableProps = {
  data: CrawlRecord[];
};

const ResultsTable = ({ data }: ResultsTableProps) => (
  <DataTable
    value={data}
    paginator
    rows={30}
    showGridlines
    stripedRows
    totalRecords={data?.length || 0}
    sortMode="multiple"
    size="small"
    emptyMessage="Scan a URL to see the results"
    responsiveLayout="scroll"
  >
    <Column
      field="title"
      header="Page Title"
      sortable
      style={{ wordBreak: "break-word" }}
    />
    <Column
      field="url"
      header="URL"
      sortable
      style={{ wordBreak: "break-word" }}
    />
    <Column field="status" header="Code" sortable />
    <Column field="size" header="Size" sortable />
  </DataTable>
);

export default ResultsTable;
