import React, { useEffect, useState } from 'react';
import { fetchDrugs } from '../api';

export default function DrugLibrary() {
  const [drugs, setDrugs] = useState<any[]>([]);

  useEffect(() => {
    fetchDrugs().then(setDrugs).catch(console.error);
  }, []);

  return (
    <div>
      <div className="header">
        <h1 className="title">Drug Library</h1>
        <button className="btn">Add New Drug</button>
      </div>
      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>MW</th>
                <th>Tm (°C)</th>
                <th>Tg (°C)</th>
                <th>BCS</th>
                <th>HSP (δD/δP/δH)</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {drugs.map(drug => (
                <tr key={drug.id}>
                  <td>{drug.id}</td>
                  <td>{drug.name}</td>
                  <td>{drug.molecular_weight}</td>
                  <td>{drug.tm}</td>
                  <td>{drug.tg}</td>
                  <td>{drug.bcs_class}</td>
                  <td>{drug.hsp_d} / {drug.hsp_p} / {drug.hsp_h}</td>
                  <td>
                    <span className={`badge ${drug.is_reference ? 'success' : 'primary'}`}>
                      {drug.is_reference ? 'Reference' : 'User'}
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
