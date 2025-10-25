import React from "react";

function Results({ results, title }) {
  if (!results || results.length === 0) return null;

  return (
    <div className="mt-4 bg-white p-4 rounded-lg shadow-md">
      <h2 className="text-lg font-semibold mb-3">{title}</h2>
      {results.map((r, idx) => (
        <div key={idx} className="mb-3 border-b pb-2">
          <a
            href={r.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 font-semibold hover:underline"
          >
            {r.title}
          </a>
          <p className="text-gray-700">{r.content}</p>
        </div>
      ))}
    </div>
  );
}

export default Results;
