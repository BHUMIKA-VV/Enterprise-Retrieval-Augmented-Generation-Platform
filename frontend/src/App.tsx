import ChatWindow from "./components/ChatWindow";
import UploadPanel from "./components/UploadPanel";
import "./styles.css";

import KnowledgeBasePage from "./pages/KnowledgeBasePage";


// =========================
// 聊天首页
// =========================
function HomePage() {

    return (
        <div className="layout">

            {/* 左侧上传 */}
            <div className="sidebar">
                <UploadPanel />
            </div>

            {/* 右侧聊天 */}
            <ChatWindow />

        </div>
    );
}

// =========================
// 简易路由
// =========================
export default function App() {

    const path = window.location.pathname;

    // http://localhost:5173/kb
    if (path === "/kb") {
        return <KnowledgeBasePage />;
    }

    // 默认首页
    return <HomePage />;
}