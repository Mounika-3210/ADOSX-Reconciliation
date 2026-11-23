
import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

const API = (
  (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
) + '/api';

function App() {
  const [orgs, setOrgs] = useState([]);
  const [org, setOrg] = useState('');
  const [data, setData] = useState([]);
  const [reasons, setReasons] = useState([]);
  const [reason, setReason] = useState('');
  const [sort, setSort] = useState('record_id');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');

  // Load organizations when the application starts
  useEffect(() => {
    fetch(`${API}/orgs/`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to load organizations');
        }
        return response.json();
      })
      .then((result) => {
        const organizations = result.orgs || [];
        setOrgs(organizations);

        if (organizations.length > 0) {
          setOrg(organizations[0]);
        }
      })
      .catch(() => {
        setError('Cannot reach backend. Start Django on port 8000.');
      });
  }, []);

  // Fetch reconciliation results
  const load = async () => {
    if (!org) return;

    setLoading(true);
    setError('');

    try {
      const url = `${API}/discrepancies/?org=${encodeURIComponent(org)}&sort=${encodeURIComponent(sort)}`;
      const response = await fetch(url);
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Request failed');
      }

      setData(result.results || []);
      setReasons(result.reasons || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Reload when organization or sorting changes
  useEffect(() => {
    if (org) {
      load();
    }
  }, [org, sort]);

  // Filter records by disagreement reason
  const filtered = useMemo(() => {
    if (!reason) return data;
    return data.filter((row) => row.reason === reason);
  }, [data, reason]);

  // Upload CSV files
  async function upload(e) {
    e.preventDefault();

    const form = new FormData();

    ['system_a', 'system_b', 'locations'].forEach((key) => {
      const file = e.target[key].files[0];
      if (file) {
        form.append(key, file);
      }
    });

    setLoading(true);
    setStatus('');
    setError('');

    try {
      const response = await fetch(`${API}/import/`, {
        method: 'POST',
        body: form,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Import failed');
      }

      setStatus(
        `Imported ${result.imported.system_a} System A rows, ${result.imported.system_b} System B rows, and ${result.imported.locations} locations.`
      );

      e.target.reset();
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // Display empty values clearly
  const value = (v) => {
    if (v === null || v === undefined || v === '') {
      return '—';
    }
    return v;
  };

  return (
    <div className="app">
      <header>
        <div className="brand">
          A<span>·</span> reconciliation
        </div>
        <div className="tag">DATA QUALITY CONSOLE</div>
      </header>

      <main>
        <section className="intro">
          <div className="eyebrow">ADOSX ENGINEERING · TAKE-HOME</div>
          <h1>System reconciliation</h1>
          <p>
            Review records that disagree between System A and System B.
            Tenant data is scoped by location ownership.
          </p>
        </section>

        <section className="controls">
          <label>
            Organization / tenant
            <select
              value={org}
              onChange={(e) => {
                setOrg(e.target.value);
                setReason('');
              }}
            >
              <option value="">Select organization</option>
              {orgs.map((organization) => (
                <option key={organization} value={organization}>
                  {organization}
                </option>
              ))}
            </select>
          </label>

          <label>
            Disagreement type
            <select
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            >
              <option value="">All types</option>
              {reasons.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label>
            Sort by
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value)}
            >
              <option value="record_id">Record ID</option>
              <option value="system_a_value">System A value</option>
              <option value="system_b_value">System B value</option>
              <option value="reason">Reason</option>
              <option value="location_name">Location</option>
            </select>
          </label>

          <button className="refresh" onClick={load} disabled={loading}>
            Refresh
          </button>
        </section>

        <section className="summary">
          <div>
            <span>Disagreements shown</span>
            <strong>{filtered.length}</strong>
          </div>
          <div>
            <span>Tenant</span>
            <strong>{org || '—'}</strong>
          </div>
          <div>
            <span>Detected categories</span>
            <strong>{reasons.length}</strong>
          </div>
        </section>

        {error && <div className="alert error">{error}</div>}
        {status && <div className="alert success">{status}</div>}

        <section className="table-wrap">
          <div className="table-head">
            <h2>Disagreement records</h2>
            <span>{filtered.length} results</span>
          </div>

          <div className="scroll">
            <table>
              <thead>
                <tr>
                  <th>Record ID</th>
                  <th>Reason</th>
                  <th>System A value</th>
                  <th>System B value</th>
                  <th>System A date</th>
                  <th>System B date</th>
                  <th>Location</th>
                  <th>Details</th>
                </tr>
              </thead>

              <tbody>
                {filtered.map((r, i) => (
                  <tr key={`${r.record_id}-${r.reason}-${i}`}>
                    <td className="mono">{value(r.record_id)}</td>
                    <td>
                      <span className="badge">{r.reason}</span>
                    </td>
                    <td>{value(r.system_a_value)}</td>
                    <td>{value(r.system_b_value)}</td>
                    <td>{value(r.system_a_date)}</td>
                    <td>{value(r.system_b_date)}</td>
                    <td>{value(r.location_name || r.location_id)}</td>
                    <td className="details">{value(r.detail)}</td>
                  </tr>
                ))}

                {!loading && filtered.length === 0 && (
                  <tr>
                    <td colSpan="8" className="empty">
                      No disagreements found for this filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {loading && <div className="loading">Loading records…</div>}
        </section>

        <section className="import">
          <h2>Import assessment CSVs</h2>
          <p>
            Import the three source files to replace the current database
            contents. All source rows are retained, including rows with
            messy values or missing identifiers.
          </p>

          <form onSubmit={upload}>
            <div className="files">
              {[
                ['system_a', 'System A CSV'],
                ['system_b', 'System B CSV'],
                ['locations', 'Locations CSV'],
              ].map(([name, label]) => (
                <label key={name}>
                  {label}
                  <input
                    name={name}
                    type="file"
                    accept=".csv"
                    required
                  />
                </label>
              ))}
            </div>

            <button type="submit" disabled={loading}>
              {loading ? 'Processing…' : 'Import CSV files'}
            </button>
          </form>
        </section>

        <footer>
          ADOSX Reconciliation · Tenant-safe comparison · Local assessment build
        </footer>
      </main>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
