import { useEffect, useState } from "react";

const API_BASE = "http://localhost:8000";

function StatCard({ title, value }) {
    return (
        <div
            style={{
                background: "#fff",
                border: "1px solid #e8e8e8",
                borderRadius: "12px",
                padding: "20px",
                minWidth: "180px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.04)"
            }}
        >
            <div style={{ fontSize: 13, color: "#888" }}>
                {title}
            </div>

            <div
                style={{
                    fontSize: 28,
                    fontWeight: 700,
                    marginTop: 10
                }}
            >
                {value}
            </div>
        </div>
    );
}

export default function KnowledgeBasePage() {

    const [stats, setStats] = useState(null);
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // =========================
    // load data
    // =========================
    const loadData = async () => {

        try {

            setLoading(true);
            setError("");

            const [statsRes, filesRes] = await Promise.all([
                fetch(`${API_BASE}/api/debug/stats`),
                fetch(`${API_BASE}/api/debug/files`)
            ]);

            const statsData = await statsRes.json();
            const filesData = await filesRes.json();

            setStats(statsData);
            setFiles(filesData.data || []);

        } catch (err) {

            console.error(err);
            setError("Failed to load knowledge base.");

        } finally {
            setLoading(false);
        }
    };

    // =========================
    // delete file
    // =========================
    const handleDeleteFile = async (source, kbName) => {

        const ok = window.confirm(`Delete file?\n\n${source}`);
        if (!ok) return;

        try {

            await fetch(
                `${API_BASE}/api/debug/file?source=${encodeURIComponent(source)}&kb_name=${kbName}`,
                { method: "DELETE" }
            );

            await loadData();

        } catch (err) {
            alert("Delete failed");
        }
    };

    // =========================
    // clear KB
    // =========================
    const handleClearKB = async () => {

        const ok = window.confirm("Delete ALL documents in default KB?");
        if (!ok) return;

        try {

            await fetch(
                `${API_BASE}/api/debug/kb?kb_name=default`,
                { method: "DELETE" }
            );

            await loadData();

        } catch (err) {
            alert("Clear failed");
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    return (

        <div
            style={{
                minHeight: "100vh",
                background: "#f6f7fb",
                padding: "40px",
                color: "#333"
            }}
        >

            <div style={{ maxWidth: "1200px", margin: "0 auto" }}>

                {/* header */}
                <div style={{ marginBottom: 25 }}>
                    <h1 style={{ margin: 0 }}>
                        Knowledge Base Manager
                    </h1>
                    <p style={{ color: "#777", marginTop: 6 }}>
                        Manage documents stored in Milvus vector database
                    </p>
                </div>

                {/* stats */}
                {stats && (
                    <div
                        style={{
                            display: "flex",
                            gap: 16,
                            marginBottom: 25,
                            flexWrap: "wrap"
                        }}
                    >
                        <StatCard title="Documents" value={stats.documents} />
                        <StatCard title="Chunks" value={stats.chunks} />
                        <StatCard title="KB Count" value={stats.kb_count} />
                    </div>
                )}

                {/* actions */}
                <div
                    style={{
                        display: "flex",
                        gap: 10,
                        marginBottom: 20
                    }}
                >
                    <button
                        onClick={loadData}
                        style={{
                            background: "#1677ff",
                            color: "#fff",
                            border: "none",
                            padding: "10px 16px",
                            borderRadius: "8px",
                            cursor: "pointer"
                        }}
                    >
                        Refresh
                    </button>

                    <button
                        onClick={handleClearKB}
                        style={{
                            background: "#ff4d4f",
                            color: "#fff",
                            border: "none",
                            padding: "10px 16px",
                            borderRadius: "8px",
                            cursor: "pointer"
                        }}
                    >
                        Clear KB
                    </button>
                </div>

                {/* loading */}
                {loading && (
                    <div style={{ marginBottom: 15 }}>
                        Loading...
                    </div>
                )}

                {/* error */}
                {error && (
                    <div style={{ color: "red", marginBottom: 15 }}>
                        {error}
                    </div>
                )}

                {/* file list */}
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>

                    {files.length === 0 && !loading ? (
                        <div
                            style={{
                                background: "#fff",
                                padding: 25,
                                borderRadius: 12,
                                border: "1px solid #eee",
                                textAlign: "center",
                                color: "#888"
                            }}
                        >
                            No files found
                        </div>
                    ) : (
                        files.map((file, index) => (
                            <div
                                key={index}
                                style={{
                                    background: "#fff",
                                    border: "1px solid #eee",
                                    borderRadius: 12,
                                    padding: 18,
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center"
                                }}
                            >

                                {/* left */}
                                <div>
                                    <div style={{ fontWeight: 600, fontSize: 16 }}>
                                        📄 {file.source}
                                    </div>

                                    <div style={{ fontSize: 13, color: "#666", marginTop: 6 }}>
                                        KB: {file.kb_name}
                                    </div>

                                    <div style={{ fontSize: 13, color: "#666" }}>
                                        Chunks: {file.chunks}
                                    </div>
                                </div>

                                {/* right */}
                                <button
                                    onClick={() =>
                                        handleDeleteFile(file.source, file.kb_name)
                                    }
                                    style={{
                                        background: "#ff4d4f",
                                        color: "#fff",
                                        border: "none",
                                        padding: "8px 14px",
                                        borderRadius: 8,
                                        cursor: "pointer"
                                    }}
                                >
                                    Delete
                                </button>

                            </div>
                        ))
                    )}

                </div>

            </div>

        </div>
    );
}