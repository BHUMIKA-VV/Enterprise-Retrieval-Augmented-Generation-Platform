import { useEffect, useRef, useState } from "react";
import Message from "./Message.tsx";

import {
    chatRequest,
    uploadAuditFile
} from "../api/client";

export default function ChatWindow() {

    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [attachments, setAttachments] = useState([]);

    const boxRef = useRef(null);

    const handleFileUpload = async (e) => {

        const files = Array.from(e.target.files || []);
        e.target.value = "";

        for (const file of files) {

            const tempId = Date.now() + Math.random();

            setAttachments(prev => [
                ...prev,
                {
                    id: tempId,
                    file_name: file.name,
                    file_path: null,
                    status: "uploading"
                }
            ]);

            try {

                const result =
                    await uploadAuditFile(file);

                setAttachments(prev =>
                    prev.map(item =>
                        item.id === tempId
                            ? {
                                ...item,
                                file_path: result.file_path,
                                status: "done"
                            }
                            : item
                    )
                );

            } catch (err) {

                console.error(err);

                setAttachments(prev =>
                    prev.map(item =>
                        item.id === tempId
                            ? {
                                ...item,
                                status: "error"
                            }
                            : item
                    )
                );
            }
        }
    };

    const send = async () => {

        if (!input.trim()) return;

        const userText = input;

        setInput("");

        setMessages(prev => [
            ...prev,
            {
                role: "user",
                content: userText
            }
        ]);

        const payload = {
            query: userText,
            conversation_id: 1,

            attachments: attachments
                .filter(a => a.file_path)
                .map(a => ({
                    file_name: a.file_name,
                    file_path: a.file_path
                }))
        };

        console.log(
            "CHAT PAYLOAD =",
            payload
        );

        try {

            const res =
                await chatRequest(payload);

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: res.answer,
                    mode: res.mode,
                    sources: res.sources
                }
            ]);

            setAttachments([]);

        } catch (err) {

            console.error(err);

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: "请求失败"
                }
            ]);
        }
    };

    useEffect(() => {

        boxRef.current?.scrollTo(
            0,
            boxRef.current.scrollHeight
        );

    }, [messages]);

    return (
        <div className="main">

            <div
                className="chat-box"
                ref={boxRef}
            >
                {messages.map((m, i) => (
                    <Message
                        key={i}
                        msg={m}
                    />
                ))}
            </div>

            <div className="input-wrapper">

                {attachments.length > 0 && (
                    <div className="attachment-bar">

                        {attachments.map(file => (

                            <div
                                key={file.id}
                                className="attachment-item"
                            >
                                📄 {file.file_name}

                                {file.status === "uploading" && " ⏳"}
                                {file.status === "done" && " ✔"}
                                {file.status === "error" && " ❌"}

                                <span
                                    onClick={() =>
                                        setAttachments(prev =>
                                            prev.filter(
                                                i => i.id !== file.id
                                            )
                                        )
                                    }
                                    style={{
                                        marginLeft: 8,
                                        cursor: "pointer"
                                    }}
                                >
                                    ×
                                </span>

                            </div>

                        ))}

                    </div>
                )}

                <div className="input-box">

                    <label className="text-btn">

                        Upload

                        <input
                            type="file"
                            multiple
                            onChange={handleFileUpload}
                            style={{
                                display: "none"
                            }}
                        />

                    </label>

                    <input
                        value={input}
                        onChange={(e) =>
                            setInput(e.target.value)
                        }
                        onKeyDown={(e) =>
                            e.key === "Enter" && send()
                        }
                        placeholder="Message..."
                    />

                    <button onClick={send}>
                        Send
                    </button>

                </div>

            </div>

        </div>
    );
}