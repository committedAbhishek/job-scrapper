import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);

  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");
  const [companyFilter, setCompanyFilter] = useState("");

  const [page, setPage] = useState(0);
  const limit = 10;

  const fetchJobs = async () => {
    const offset = page * limit;

    let url = `${API_BASE}/jobs?limit=${limit}&offset=${offset}`;

    if (statusFilter) url += `&status=${statusFilter}`;
    if (search) url += `&keyword=${search}`;
    if (companyFilter) url += `&company=${companyFilter}`;

    const res = await fetch(url);
    const data = await res.json();

    setJobs(data.data);
    setTotal(data.total);
  };

  const scrapeJobs = async () => {
    await fetch(`${API_BASE}/scrape-all`, { method: "POST" });
    fetchJobs();
  };

  const updateStatus = async (id, status) => {
    await fetch(`${API_BASE}/jobs/${id}/status?status=${status}`, {
      method: "PATCH",
    });
    fetchJobs();
  };

  useEffect(() => {
    fetchJobs();
  }, [statusFilter, search, companyFilter, page]);

  const totalPages = Math.ceil(total / limit);

  const newCount = jobs.filter(j => j.status === "new").length;
  const appliedCount = jobs.filter(j => j.status === "applied").length;
  const ignoredCount = jobs.filter(j => j.status === "ignored").length;

  return (
  <div className="page">
    <div className="container">

      {/* Header */}
      <div className="header">
        <h1>Job Dashboard</h1>
        <button className="primary-btn" onClick={scrapeJobs}>
          Scrape Now
        </button>
      </div>
      {/* Stats */}
<div className="stats">
  <div className="stat-card">
    <span className="stat-label">New</span>
    <span className="stat-value">{newCount}</span>
  </div>

  <div className="stat-card">
    <span className="stat-label">Applied</span>
    <span className="stat-value">{appliedCount}</span>
  </div>

  <div className="stat-card">
    <span className="stat-label">Ignored</span>
    <span className="stat-value">{ignoredCount}</span>
  </div>
</div>

      {/* Filters */}
      <div className="filters">
        <select onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All Status</option>
          <option value="new">New</option>
          <option value="applied">Applied</option>
          <option value="ignored">Ignored</option>
        </select>

        <input
          type="text"
          placeholder="Search title..."
          onChange={(e) => setSearch(e.target.value)}
        />

        <input
          type="text"
          placeholder="Company..."
          onChange={(e) => setCompanyFilter(e.target.value)}
        />
      </div>

      {/* Info */}
      <p className="info">
        Total Jobs: {total} | Page {page + 1} of {totalPages || 1}
      </p>

      {/* Table */}
      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Title</th>
              <th>Status</th>
              <th>Actions</th>
              <th>Apply</th>
            </tr>
          </thead>

          <tbody>
            {jobs.map((job) => (
              <tr key={job.id}>
                <td>{job.company}</td>
                <td>{job.title}</td>
                <td>
                  <span className={`badge ${job.status}`}>
                    {job.status}
                  </span>
                </td>
                <td className="actions">
                  <button
                    className="action applied"
                    onClick={() => updateStatus(job.id, "applied")}
                  >
                    Applied
                  </button>

                  <button
                    className="action ignore"
                    onClick={() => updateStatus(job.id, "ignored")}
                  >
                    Ignore
                  </button>

                  <button
                    className="action reset"
                    onClick={() => updateStatus(job.id, "new")}
                  >
                    Reset
                  </button>
                </td>
                <td>
                  <a href={job.url} target="_blank" rel="noreferrer">
                    Open
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="pagination">
        <button
          disabled={page === 0}
          onClick={() => setPage(page - 1)}
        >
          Prev
        </button>

        <button
          disabled={page + 1 >= totalPages}
          onClick={() => setPage(page + 1)}
        >
          Next
        </button>
      </div>

    </div>
  </div>
);
}

export default App;