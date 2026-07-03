export default function Message({ msg }) {

    const isUser = msg.role === "user";

    return (
        <div className={`message ${isUser ? "user" : "assistant"}`}>

            <div className="bubble">

                {/* 主内容 */}
                <div
                    style={{
                        whiteSpace: "pre-wrap",
                        wordBreak: "break-word",
                        lineHeight: 1.6
                    }}
                >
                    {msg.content}
                </div>

                {/* 附件展示 */}
                {msg.attachments?.length > 0 && (
                    <div
                        style={{
                            marginTop: 8,
                            display: "flex",
                            flexWrap: "wrap",
                            gap: 6
                        }}
                    >
                        {msg.attachments.map((a, i) => (
                            <div
                                key={i}
                                style={{
                                    fontSize: 12,
                                    background: "#f2f2f2",
                                    padding: "3px 6px",
                                    borderRadius: 6,
                                    opacity: 0.85
                                }}
                            >
                                📎 {a.file_name}
                            </div>
                        ))}
                    </div>
                )}

                {/* mode */}
                {msg.mode && (
                    <div
                        style={{
                            fontSize: 11,
                            opacity: 0.5,
                            marginTop: 8
                        }}
                    >
                        {msg.mode.toUpperCase()}
                    </div>
                )}

                {/* sources */}
                {msg.sources?.length > 0 && (
                    <div
                        style={{
                            fontSize: 11,
                            marginTop: 8,
                            color: "#10a37f"
                        }}
                    >
                        Sources:
                        <ul
                            style={{
                                margin: "4px 0 0 16px",
                                padding: 0
                            }}
                        >
                            {msg.sources.map((source, index) => (
                                <li key={index}>
                                    {source}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

            </div>

        </div>
    );
}