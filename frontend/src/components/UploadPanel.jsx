import { useState } from "react";
import { uploadRuleFile } from "../api/client";

export default function UploadPanel() {

    const [kbName, setKbName] = useState("default");
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState("");
    const [files, setFiles] = useState([]);

    // =========================
    // 选择文件（不上传）
    // =========================
    const handleSelectFile = (e) => {

        const selected = Array.from(e.target.files || []);

        if (!selected.length) return;

        setFiles(selected);

        // 允许重复选同一个文件
        e.target.value = "";
    };

    // =========================
    // 上传（规则库：入向量库）
    // =========================
    const handleUpload = async () => {

        if (files.length === 0) return;

        setUploading(true);
        setMessage("");

        try {

            for (const file of files) {

                const result = await uploadRuleFile(
                    file,
                    kbName
                );

                console.log(
                    "RULE UPLOAD RESULT:",
                    result
                );
            }

            setMessage("上传成功");

            // 清空文件
            setFiles([]);

        } catch (err) {

            console.error(err);
            setMessage("上传失败");

        } finally {

            setUploading(false);
        }
    };

    return (
        <div className="sidebar-card">

            {/* 标题 */}
            <div className="sidebar-title">
                Knowledge Base
            </div>

            <div className="sidebar-section">

                {/* KB Name */}
                <input
                    className="sidebar-input"
                    value={kbName}
                    onChange={(e) =>
                        setKbName(e.target.value)
                    }
                    placeholder="KB name"
                />

                {/* 文件选择 */}
                <input
                    type="file"
                    multiple
                    onChange={handleSelectFile}
                    className="sidebar-input"
                />

                {/* 上传按钮 */}
                <button
                    className="sidebar-button"
                    onClick={handleUpload}
                    disabled={uploading}
                >
                    {uploading
                        ? "Uploading..."
                        : "Upload Rules"}
                </button>

                {/* 已选文件列表 */}
                {files.length > 0 && (
                    <div className="file-list">

                        {files.map((f, i) => (
                            <div
                                key={i}
                                className="file-item"
                            >
                                📄 {f.name}
                            </div>
                        ))}

                    </div>
                )}

                {/* 状态提示 */}
                {message && (
                    <div className="upload-msg">
                        {message}
                    </div>
                )}

            </div>
        </div>
    );
}