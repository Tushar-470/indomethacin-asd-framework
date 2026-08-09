import React, { useEffect, useState } from 'react';
import { fetchPolymers } from '../api';

export default function PolymerLibrary() {
  const [polymers, setPolymers] = useState<any[]>([]);

  useEffect(() => {
    fetchPolymers().then(setPolymers).catch(console.error);
  }, []);

  return (
    <div>
      <div className="header">
        <h1 className="title">Polymer Library</h1>
        <button className="btn">Add New Polymer</button>
      </div>
      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Abbreviation</th>
                <th>Mn</th>
                <th>Tg (°C)</th>
                <th>HSP (δD/δP/δH)</th>
                <th>Evidence Score</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {polymers.map(poly => (
                <tr key={poly.id}>
                  <td>{poly.id}</td>
                  <td>{poly.name}</td>
                  <td>{poly.abbreviation}</td>
                  <td>{poly.molecular_weight}</td>
                  <td>{poly.tg}</td>
                  <td>{poly.hsp_d} / {poly.hsp_p} / {poly.hsp_h}</td>
                  <td>{poly.evidence_score}</td>
                  <td>
                    <span className={`badge ${poly.is_reference ? 'success' : 'primary'}`}>
                      {poly.is_reference ? 'Reference' : 'User'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
