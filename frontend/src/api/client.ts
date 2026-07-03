const BASE_URL = "http://localhost:8000";

export async function chatRequest(payload) {

    const res = await fetch(
        `${BASE_URL}/api/chat`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        }
    );

    return await res.json();
}


// =========================
// Audit上传
// 不入向量库
// =========================
export async function uploadAuditFile(file) {

    const form = new FormData();

    form.append("file", file);

    const res = await fetch(
        `${BASE_URL}/api/upload/audit`,
        {
            method: "POST",
            body: form
        }
    );

    return await res.json();
}


// =========================
// Rules上传
// 入向量库
// =========================
export async function uploadRuleFile(
    file,
    kbName = "default"
) {

    const form = new FormData();

    form.append("file", file);
    form.append("kb_name", kbName);

    const res = await fetch(
        `${BASE_URL}/api/upload/rules`,
        {
            method: "POST",
            body: form
        }
    );

    return await res.json();
}