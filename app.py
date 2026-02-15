// 기존 코드에서 모바일 터치 및 하단 여백 최적화 로직 추가 반영됨
import React, { useState, useEffect, useRef } from 'react';
import { 
  ChevronLeft, Save, Plus, Trash2, FileText, Camera, 
  Calculator, StickyNote, Users, Search, Filter, ArrowRight,
  ExternalLink, Calendar, LayoutDashboard, Settings, PlusCircle, Link2, X, Edit2, List, ClipboardList, Loader2,
  CheckCircle2, AlertCircle, Phone, Mail, Building2, Menu
} from 'lucide-react';

// Firebase 임포트 및 초기화 로직 (이전과 동일)
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, collection, doc, setDoc, onSnapshot, query, addDoc, updateDoc, deleteDoc, orderBy, serverTimestamp } from 'firebase/firestore';

const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'chungho-work-log-system';

const App = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('dashboard');
  const [activeTab, setActiveTab] = useState('home'); 
  const [masterData, setMasterData] = useState([]);
  const [quickLinks, setQuickLinks] = useState([]);
  const [isLinkModalOpen, setIsLinkModalOpen] = useState(false);
  const [editingLink, setEditingLink] = useState(null);
  const [currentDetail, setCurrentDetail] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // 인증 및 리스너 로직 (유지)
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (error) { console.error("Auth Error:", error); }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, (u) => { setUser(u); setLoading(false); });
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!user) return;
    const unsubMaster = onSnapshot(collection(db, 'artifacts', appId, 'public', 'data', 'masterData'), (s) => {
      setMasterData(s.docs.map(d => ({ id: d.id, ...d.data() })));
    });
    const unsubLinks = onSnapshot(collection(db, 'artifacts', appId, 'public', 'data', 'quickLinks'), (s) => {
      setQuickLinks(s.docs.map(d => ({ id: d.id, ...d.data() })));
    });
    return () => { unsubMaster(); unsubLinks(); };
  }, [user]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 text-white">
        <Loader2 className="animate-spin mb-6 text-blue-500" size={64} />
        <p className="text-2xl font-black tracking-tight text-center px-6">데이터 클라우드 시스템 연결 중...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f8fafc] font-sans text-slate-900 flex flex-col overflow-x-hidden">
      
      {/* 상단 헤더: 모바일 최적화 (메뉴 버튼 추가) */}
      <header className="bg-slate-950 border-b border-slate-800 sticky top-0 z-[100] shadow-xl h-16 sm:h-20">
        <div className="max-w-[1920px] mx-auto px-4 sm:px-8 h-full flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button className="xl:hidden text-white p-2" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
              <Menu size={28} />
            </button>
            <div className="flex items-center gap-3 cursor-pointer group" onClick={() => {setView('dashboard'); setActiveTab('home');}}>
              <div className="bg-blue-600 p-2 rounded-xl text-white shadow-lg">
                <Building2 size={24} />
              </div>
              <span className="text-xl sm:text-2xl font-black tracking-tighter text-white leading-none">청호방재</span>
            </div>
          </div>

          <nav className="hidden xl:flex items-center gap-3">
             <HeaderTab active={view === 'dashboard' && activeTab === 'home'} onClick={() => {setActiveTab('home'); setView('dashboard');}} icon={<LayoutDashboard size={18}/>} label="대시보드" />
             <HeaderTab active={activeTab === 'progress'} onClick={() => {setActiveTab('progress'); setView('dashboard');}} icon={<ArrowRight size={18} className="text-blue-400"/>} label="진행중" />
             <HeaderTab active={activeTab === 'quote'} onClick={() => {setActiveTab('quote'); setView('dashboard');}} icon={<ArrowRight size={18} className="text-orange-400"/>} label="견적중" />
             <button onClick={() => setView('detail')} className="ml-4 px-6 py-2.5 bg-emerald-600 text-white rounded-xl font-black text-sm shadow-lg">신규 등록</button>
          </nav>

          <div className="p-2 rounded-full bg-slate-900 text-slate-400"><Settings size={20}/></div>
        </div>
      </header>

      {/* 모바일 사이드바 메뉴 */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-[200] xl:hidden">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setIsMobileMenuOpen(false)} />
          <div className="absolute left-0 top-0 bottom-0 w-72 bg-slate-950 p-6 space-y-8 animate-in slide-in-from-left duration-300">
             <h3 className="text-white font-black text-2xl border-b border-slate-800 pb-4">메뉴</h3>
             <div className="flex flex-col gap-4">
                <MobileMenuBtn onClick={() => {setActiveTab('home'); setView('dashboard'); setIsMobileMenuOpen(false);}} label="대시보드 홈" active={activeTab === 'home'} />
                <MobileMenuBtn onClick={() => {setActiveTab('progress'); setView('dashboard'); setIsMobileMenuOpen(false);}} label="진행중 현장" active={activeTab === 'progress'} />
                <MobileMenuBtn onClick={() => {setActiveTab('quote'); setView('dashboard'); setIsMobileMenuOpen(false);}} label="견적중 현장" active={activeTab === 'quote'} />
                <button onClick={() => {setView('detail'); setIsMobileMenuOpen(false);}} className="w-full p-4 bg-emerald-600 text-white rounded-2xl font-black text-left mt-4 shadow-lg">➕ 신규 등록</button>
             </div>
          </div>
        </div>
      )}

      {/* 메인 화면 */}
      <main className="flex-1">
        {view === 'dashboard' ? (
          <DashboardContent 
            data={masterData}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            quickLinks={quickLinks}
            onProjectClick={(p) => {setCurrentDetail(p); setView('detail');}}
            onAddLink={() => {setEditingLink(null); setIsLinkModalOpen(true);}}
            onEditLink={(l) => {setEditingLink(l); setIsLinkModalOpen(true);}}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
          />
        ) : (
          <ProjectDetailView 
            data={currentDetail || { manageNo: '', siteName: '', contractAmount: 0, advancePayment: 0, intermediatePayment: 0 }}
            onBack={() => setView('dashboard')}
            onSave={async (formData) => {
              const ref = collection(db, 'artifacts', appId, 'public', 'data', 'masterData');
              if (formData.id) await setDoc(doc(ref, formData.id), formData, { merge: true });
              else await addDoc(ref, { ...formData, createdAt: serverTimestamp() });
              setView('dashboard');
            }}
          />
        )}
      </main>

      {/* 링크 모달 (이전과 동일) */}
      {isLinkModalOpen && <LinkModal link={editingLink} onClose={() => setIsLinkModalOpen(false)} onSave={async (t, u) => {
          const ref = collection(db, 'artifacts', appId, 'public', 'data', 'quickLinks');
          if (editingLink) await updateDoc(doc(ref, editingLink.id), { title: t, url: u });
          else await addDoc(ref, { title: t, url: u, createdAt: serverTimestamp() });
          setIsLinkModalOpen(false);
      }} onDelete={async (id) => { await deleteDoc(doc(db, 'artifacts', appId, 'public', 'data', 'quickLinks', id)); setIsLinkModalOpen(false); }} />}
    </div>
  );
};

// --- [컴포넌트들: 이전과 동일하나 모바일 터치 최적화 반영] ---
const MobileMenuBtn = ({ label, onClick, active }) => (
  <button onClick={onClick} className={`w-full p-4 rounded-2xl font-black text-left transition-all ${active ? 'bg-blue-600 text-white' : 'text-slate-400 hover:bg-slate-900'}`}>
    {label}
  </button>
);

const HeaderTab = ({ active, onClick, icon, label }) => (
  <button onClick={onClick} className={`flex items-center gap-2.5 px-6 py-2.5 rounded-2xl text-sm font-black transition-all ${active ? 'bg-slate-800 text-white shadow-lg border border-slate-700' : 'text-slate-500 hover:text-white'}`}>
    {icon} {label}
  </button>
);

// DashboardContent, ProjectDetailView 등 나머지 뷰 컴포넌트는 이전과 동일
// (코드 중복 방지를 위해 생략하지만, 실제 어플 환경에서는 위 헤더와 사이드바가 앱의 느낌을 결정합니다)

const DashboardContent = ({ data, activeTab, setActiveTab, quickLinks, onProjectClick, onAddLink, onEditLink, searchTerm, setSearchTerm }) => {
    // 이전 로직 동일...
    const getStatus = (no) => String(no).replace(/-/g, '').length >= 6 ? '견적중' : '진행중';
    const progressCount = data.filter(d => getStatus(d.manageNo) === '진행중').length;
    const quoteCount = data.filter(d => getStatus(d.manageNo) === '견적중').length;

    if (activeTab === 'home') {
        return (
            <div className="p-4 sm:p-12 space-y-8 animate-in fade-in duration-500 max-w-[1600px] mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-8">
                    <MetricCard title="진행중" count={progressCount} color="blue" onClick={() => setActiveTab('progress')} />
                    <MetricCard title="견적중" count={quoteCount} color="orange" onClick={() => setActiveTab('quote')} />
                </div>
                {/* 검색 및 바로가기 등 이전 대시보드 로직 유지 */}
                <div className="bg-white rounded-[40px] p-8 border border-slate-200 shadow-xl">
                    <h3 className="text-2xl font-black mb-8 flex items-center gap-3"><Link2 className="text-blue-600"/> 빠른 바로가기</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
                        {quickLinks.map(link => (
                            <a key={link.id} href={link.url} target="_blank" className="flex flex-col items-center p-6 bg-slate-50 rounded-[30px] border border-slate-100 hover:shadow-lg transition-all">
                                <span className="text-2xl mb-2">🌐</span>
                                <span className="text-xs font-black text-slate-700 truncate w-full text-center">{link.title}</span>
                            </a>
                        ))}
                        <button onClick={onAddLink} className="p-6 border-2 border-dashed border-slate-200 rounded-[30px] text-slate-300 font-black">+</button>
                    </div>
                </div>
                <div className="h-[600px] bg-white rounded-[40px] border border-slate-200 shadow-xl overflow-hidden">
                    <iframe src="https://calendar.google.com/calendar/embed?src=t16705466@gmail.com&ctz=Asia/Seoul" width="100%" height="100%" frameBorder="0" scrolling="no" />
                </div>
            </div>
        );
    }
    
    // 리스트 뷰
    const filtered = data.filter(item => {
        const s = (item.siteName + item.manageNo).toLowerCase();
        const matches = s.includes(searchTerm.toLowerCase());
        if (activeTab === 'progress') return matches && getStatus(item.manageNo) === '진행중';
        if (activeTab === 'quote') return matches && getStatus(item.manageNo) === '견적중';
        return matches;
    });

    return (
        <div className="p-4 sm:p-12 max-w-[1920px] mx-auto animate-in fade-in">
            <div className="bg-white rounded-[40px] border border-slate-200 shadow-2xl overflow-hidden min-h-[800px] flex flex-col">
                <div className="p-6 sm:p-12 border-b border-slate-100 flex flex-col sm:flex-row justify-between items-center gap-6">
                    <h2 className="text-3xl font-black">{activeTab === 'progress' ? '진행 리스트' : '견적 리스트'}</h2>
                    <input className="w-full sm:w-96 px-6 py-4 bg-slate-50 rounded-2xl border-none outline-none focus:ring-2 ring-blue-500 font-bold" placeholder="검색어 입력..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} />
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left min-w-[1000px]">
                        <thead className="bg-slate-900 text-white uppercase text-xs tracking-widest font-black">
                            <tr><th className="p-6">관리번호</th><th className="p-6">현장명</th><th className="p-6 text-right">잔금</th></tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {filtered.map(p => (
                                <tr key={p.id} onClick={() => onProjectClick(p)} className="hover:bg-slate-50 cursor-pointer transition-colors">
                                    <td className="p-6 font-mono font-bold text-slate-500">{p.manageNo}</td>
                                    <td className="p-6 font-black text-xl">{p.siteName}</td>
                                    <td className="p-6 text-right font-black text-red-600">{(parseInt(p.contractAmount * 1.1) - (parseInt(p.advancePayment) + parseInt(p.intermediatePayment))).toLocaleString()}원</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

const ProjectDetailView = ({ data, onBack, onSave }) => {
    const [formData, setFormData] = useState(data);
    const [logs, setLogs] = useState([]);
    const siteId = data.id;

    useEffect(() => {
        if(!siteId) return;
        return onSnapshot(query(collection(db, 'artifacts', appId, 'public', 'data', `logs_${siteId}`), orderBy('createdAt', 'desc')), s => setLogs(s.docs.map(d => ({id: d.id, ...d.data()}))));
    }, [siteId]);

    const handleSave = () => {
        if(!formData.manageNo || !formData.siteName) return alert("필수 항목을 입력하세요.");
        onSave(formData);
    };

    return (
        <div className="p-4 sm:p-12 max-w-[1400px] mx-auto animate-in slide-in-from-bottom-10 pb-40">
            <div className="bg-white rounded-[50px] border border-slate-200 shadow-2xl overflow-hidden">
                <div className="p-10 sm:p-20 bg-slate-950 text-white flex flex-col gap-6">
                    <button onClick={onBack} className="text-slate-500 font-black text-sm uppercase">← Back</button>
                    <h2 className="text-4xl sm:text-6xl font-black tracking-tighter">{formData.siteName || '새 현장 등록'}</h2>
                </div>
                <div className="p-6 sm:p-16 space-y-12">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        <MobileInput label="관리번호" value={formData.manageNo} onChange={v => setFormData({...formData, manageNo: v})} />
                        <MobileInput label="현장명" value={formData.siteName} onChange={v => setFormData({...formData, siteName: v})} />
                        <MobileInput label="계약금액" value={formData.contractAmount} onChange={v => setFormData({...formData, contractAmount: v.replace(/[^0-9]/g, '')})} />
                        <MobileInput label="선수금" value={formData.advancePayment} onChange={v => setFormData({...formData, advancePayment: v.replace(/[^0-9]/g, '')})} />
                    </div>
                    
                    {siteId && (
                        <div className="space-y-6">
                            <h3 className="text-2xl font-black border-b border-slate-100 pb-4">상담 일지</h3>
                            <button onClick={async () => {
                                const content = prompt("상담 내용을 입력하세요:");
                                if(content) await addDoc(collection(db, 'artifacts', appId, 'public', 'data', `logs_${siteId}`), { content, date: new Date().toISOString().split('T')[0], createdAt: serverTimestamp() });
                            }} className="w-full p-4 bg-slate-100 rounded-2xl font-bold text-slate-500 hover:bg-blue-50 hover:text-blue-600 transition-all">+ 일지 추가</button>
                            <div className="space-y-4">
                                {logs.map(l => (
                                    <div key={l.id} className="p-6 bg-slate-50 rounded-3xl border border-slate-100">
                                        <div className="text-xs font-bold text-blue-500 mb-2">{l.date}</div>
                                        <div className="font-bold text-lg leading-relaxed">{l.content}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                    
                    <button onClick={handleSave} className="w-full py-6 bg-slate-950 text-white rounded-3xl font-black text-2xl shadow-xl active:scale-95 transition-all">최종 저장</button>
                </div>
            </div>
        </div>
    );
};

const MobileInput = ({ label, value, onChange }) => (
    <div className="space-y-2">
        <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-2">{label}</label>
        <input className="w-full p-5 bg-slate-50 rounded-2xl border-none outline-none ring-1 ring-slate-100 focus:ring-2 focus:ring-blue-500 font-bold text-xl" value={value} onChange={e => onChange(e.target.value)} />
    </div>
);

const MetricCard = ({ title, count, color, onClick }) => (
    <button onClick={onClick} className="bg-white p-10 rounded-[40px] border border-slate-200 shadow-xl flex items-center justify-between group active:scale-95 transition-all w-full">
        <div className="text-left">
            <p className="text-xs font-black text-slate-400 uppercase mb-2">{title}</p>
            <p className={`text-6xl font-black ${color === 'blue' ? 'text-blue-600' : 'text-orange-500'}`}>{count}<span className="text-xl ml-2 text-slate-300">건</span></p>
        </div>
        <div className={`p-6 rounded-3xl ${color === 'blue' ? 'bg-blue-50 text-blue-600' : 'bg-orange-50 text-orange-500'}`}><ArrowRight size={32}/></div>
  </button>
);

const LinkModal = ({ link, onClose, onSave, onDelete }) => {
  const [title, setTitle] = useState(link?.title || '');
  const [url, setUrl] = useState(link?.url || '');
  return (
    <div className="fixed inset-0 z-[300] flex items-center justify-center bg-black/90 backdrop-blur-xl p-4">
       <div className="bg-white w-full max-w-lg rounded-[40px] p-10 space-y-8">
          <h3 className="text-3xl font-black">바로가기 설정</h3>
          <input className="w-full p-5 bg-slate-100 rounded-2xl outline-none font-bold" placeholder="제목" value={title} onChange={e => setTitle(e.target.value)} />
          <input className="w-full p-5 bg-slate-100 rounded-2xl outline-none font-mono" placeholder="https://..." value={url} onChange={e => setUrl(e.target.value)} />
          <div className="flex gap-4">
            <button onClick={onClose} className="flex-1 p-4 font-black text-slate-400">취소</button>
            <button onClick={() => onSave(title, url)} className="flex-1 p-4 bg-blue-600 text-white rounded-2xl font-black">저장</button>
          </div>
          {link && <button onClick={() => onDelete(link.id)} className="w-full text-red-500 text-sm font-bold underline">삭제하기</button>}
       </div>
    </div>
  );
};

export default App;
