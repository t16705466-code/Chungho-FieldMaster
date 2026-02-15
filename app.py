// 기존 코드에서 모바일 터치 및 하단 여백 최적화 로직 추가 반영됨
import React, { useState, useEffect, useRef } from 'react';
import { 
  ChevronLeft, Save, Plus, Trash2, FileText, Camera, 
  Calculator, StickyNote, Users, Search, Filter, ArrowRight,
  ExternalLink, Calendar, LayoutDashboard, Settings, PlusCircle, Link2, X, Edit2, List, ClipboardList, Loader2,
  CheckCircle2, AlertCircle, Phone, Mail, Building2, Menu
} from 'lucide-react';

// Firebase 임포트 및 초기화 로직
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

  // 인증 및 리스너 로직
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
      
      {/* 상단 헤더 */}
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
             <button onClick={() => { setCurrentDetail(null); setView('detail'); }} className="ml-4 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-black text-sm shadow-lg flex items-center gap-2">
               <Plus size={18} /> 신규 등록
             </button>
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
                <button onClick={() => {setCurrentDetail(null); setView('detail'); setIsMobileMenuOpen(false);}} className="w-full p-4 bg-emerald-600 text-white rounded-2xl font-black text-left mt-4 shadow-lg flex items-center gap-2">
                  <Plus size={20} /> 신규 등록
                </button>
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
              if (formData.id) await updateDoc(doc(ref, formData.id), formData);
              else await addDoc(ref, { ...formData, createdAt: serverTimestamp() });
              setView('dashboard');
            }}
          />
        )}
      </main>

      {/* 링크 모달 */}
      {isLinkModalOpen && (
        <LinkModal 
          link={editingLink} 
          onClose={() => setIsLinkModalOpen(false)} 
          onSave={async (t, u) => {
            const ref = collection(db, 'artifacts', appId, 'public', 'data', 'quickLinks');
            if (editingLink) await updateDoc(doc(ref, editingLink.id), { title: t, url: u });
            else await addDoc(ref, { title: t, url: u, createdAt: serverTimestamp() });
            setIsLinkModalOpen(false);
          }} 
          onDelete={async (id) => { 
            await deleteDoc(doc(db, 'artifacts', appId, 'public', 'data', 'quickLinks', id)); 
            setIsLinkModalOpen(false); 
          }} 
        />
      )}
    </div>
  );
};

// --- [컴포넌트: 네비게이션/공통] ---
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

// --- [컴포넌트: 대시보드 메인] ---
const DashboardContent = ({ data, activeTab, setActiveTab, quickLinks, onProjectClick, onAddLink, onEditLink, searchTerm, setSearchTerm }) => {
    const getStatus = (no) => {
      if(!no) return '-';
      return String(no).replace(/-/g, '').length >= 6 ? '견적중' : '진행중';
    };
    const progressCount = data.filter(d => getStatus(d.manageNo) === '진행중').length;
    const quoteCount = data.filter(d => getStatus(d.manageNo) === '견적중').length;

    if (activeTab === 'home') {
        return (
            <div className="p-4 sm:p-12 space-y-8 animate-in fade-in duration-500 max-w-[1600px] mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-8">
                    <MetricCard title="진행중인 공사" count={progressCount} color="blue" onClick={() => setActiveTab('progress')} />
                    <MetricCard title="견적 및 대기" count={quoteCount} color="orange" onClick={() => setActiveTab('quote')} />
                </div>

                <div className="bg-white rounded-[40px] p-8 border border-slate-200 shadow-xl relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-2 h-full bg-blue-600" />
                    <h3 className="text-2xl font-black mb-8 flex items-center gap-3"><Link2 className="text-blue-600"/> 빠른 바로가기</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
                        {quickLinks.map(link => (
                            <div key={link.id} className="relative group">
                              <a href={link.url} target="_blank" rel="noreferrer" className="flex flex-col items-center p-6 bg-slate-50 rounded-[30px] border border-slate-100 hover:bg-white hover:border-blue-500 hover:shadow-lg transition-all h-full">
                                  <div className="w-12 h-12 rounded-2xl bg-white border border-slate-100 flex items-center justify-center text-xl mb-3">🌐</div>
                                  <span className="text-xs font-black text-slate-700 truncate w-full text-center">{link.title}</span>
                              </a>
                              <button onClick={() => onEditLink(link)} className="absolute top-2 right-2 p-1.5 bg-white rounded-full text-slate-300 hover:text-blue-500 opacity-0 group-hover:opacity-100 shadow-sm transition-opacity"><Edit2 size={12}/></button>
                            </div>
                        ))}
                        <button onClick={onAddLink} className="p-6 border-2 border-dashed border-slate-200 rounded-[30px] text-slate-300 hover:text-blue-500 hover:border-blue-200 transition-all font-black flex items-center justify-center">
                          <Plus size={32} />
                        </button>
                    </div>
                </div>

                <div className="h-[700px] bg-white rounded-[40px] border border-slate-200 shadow-xl overflow-hidden relative">
                    <div className="p-6 border-b border-slate-100 flex items-center gap-3">
                      <Calendar className="text-red-500" />
                      <span className="font-black text-slate-800">청호방재 일정표</span>
                    </div>
                    <iframe src="https://calendar.google.com/calendar/embed?src=t16705466@gmail.com&ctz=Asia/Seoul" width="100%" height="100%" frameBorder="0" scrolling="no" className="p-4" />
                </div>
            </div>
        );
    }
    
    const filtered = data.filter(item => {
        const s = (item.siteName + (item.manageNo || '')).toLowerCase();
        const matches = s.includes(searchTerm.toLowerCase());
        if (activeTab === 'progress') return matches && getStatus(item.manageNo) === '진행중';
        if (activeTab === 'quote') return matches && getStatus(item.manageNo) === '견적중';
        return matches;
    });

    return (
        <div className="p-4 sm:p-12 max-w-[1920px] mx-auto animate-in fade-in">
            <div className="bg-white rounded-[40px] border border-slate-200 shadow-2xl overflow-hidden min-h-[800px] flex flex-col">
                <div className="p-6 sm:p-12 border-b border-slate-100 flex flex-col sm:flex-row justify-between items-center gap-6 bg-slate-50/50">
                    <div className="flex items-center gap-4">
                      <div className={`p-4 rounded-2xl text-white ${activeTab === 'progress' ? 'bg-blue-600' : 'bg-orange-500'}`}><List size={28}/></div>
                      <h2 className="text-3xl font-black">{activeTab === 'progress' ? '진행 리스트' : '견적 리스트'}</h2>
                    </div>
                    <div className="relative w-full sm:w-96">
                      <Search className="absolute left-5 top-4 text-slate-400" size={20} />
                      <input className="w-full pl-14 pr-6 py-4 bg-white rounded-2xl border border-slate-200 outline-none focus:ring-2 ring-blue-500 font-bold" placeholder="현장명 검색..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} />
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left min-w-[1000px]">
                        <thead className="bg-slate-950 text-white uppercase text-xs tracking-widest font-black">
                            <tr><th className="p-6">관리번호</th><th className="p-6">현장명</th><th className="p-6 text-right">잔금</th></tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {filtered.map(p => (
                                <tr key={p.id} onClick={() => onProjectClick(p)} className="hover:bg-slate-50 cursor-pointer transition-colors group">
                                    <td className="p-6 font-mono font-bold text-slate-500">{p.manageNo}</td>
                                    <td className="p-6 font-black text-xl group-hover:text-blue-600">{p.siteName}</td>
                                    <td className="p-6 text-right font-black text-red-600">
                                      {(parseInt(p.contractAmount * 1.1 || 0) - (parseInt(p.advancePayment || 0) + parseInt(p.intermediatePayment || 0))).toLocaleString()}원
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

// --- [컴포넌트: 프로젝트 상세] ---
const ProjectDetailView = ({ data, onBack, onSave }) => {
    const [formData, setFormData] = useState(data);
    const [logs, setLogs] = useState([]);
    const siteId = data.id;

    useEffect(() => {
        if(!siteId) return;
        return onSnapshot(query(collection(db, 'artifacts', appId, 'public', 'data', `logs_${siteId}`), orderBy('createdAt', 'desc')), s => setLogs(s.docs.map(d => ({id: d.id, ...d.data()}))));
    }, [siteId]);

    const handleSave = () => {
        if(!formData.manageNo || !formData.siteName) return alert("관리번호와 현장명은 필수 항목입니다.");
        onSave(formData);
    };

    return (
        <div className="p-4 sm:p-12 max-w-[1400px] mx-auto animate-in slide-in-from-bottom-10 pb-40">
            <div className="bg-white rounded-[50px] border border-slate-200 shadow-2xl overflow-hidden">
                <div className="p-10 sm:p-20 bg-slate-950 text-white flex flex-col gap-6 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 blur-[80px]" />
                    <button onClick={onBack} className="text-slate-500 font-black text-sm uppercase hover:text-white transition-colors flex items-center gap-2"><ChevronLeft size={20}/> Back to List</button>
                    <h2 className="text-4xl sm:text-6xl font-black tracking-tighter">{formData.siteName || '새 현장 등록'}</h2>
                </div>
                <div className="p-6 sm:p-16 space-y-12">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        <MobileInput label="관리번호" value={formData.manageNo} onChange={v => setFormData({...formData, manageNo: v})} placeholder="예: 25-01" />
                        <MobileInput label="현장명" value={formData.siteName} onChange={v => setFormData({...formData, siteName: v})} placeholder="상호명 입력" />
                        <MobileInput label="계약금액(공급가)" value={formData.contractAmount} onChange={v => setFormData({...formData, contractAmount: v.replace(/[^0-9]/g, '')})} placeholder="숫자만 입력" />
                        <MobileInput label="선수금" value={formData.advancePayment} onChange={v => setFormData({...formData, advancePayment: v.replace(/[^0-9]/g, '')})} placeholder="숫자만 입력" />
                    </div>
                    
                    {siteId && (
                        <div className="space-y-6 pt-12 border-t border-slate-100">
                            <h3 className="text-2xl font-black flex items-center gap-3"><StickyNote className="text-blue-600"/> 상담 및 현장 일지</h3>
                            <button onClick={async () => {
                                const content = prompt("상담 내용을 입력하세요:");
                                if(content) await addDoc(collection(db, 'artifacts', appId, 'public', 'data', `logs_${siteId}`), { content, date: new Date().toISOString().split('T')[0], createdAt: serverTimestamp() });
                            }} className="w-full p-6 bg-blue-50 border border-blue-100 rounded-2xl font-black text-blue-600 hover:bg-blue-100 transition-all flex items-center justify-center gap-2">
                              <Plus size={24} /> 일지 내용 추가
                            </button>
                            <div className="space-y-4">
                                {logs.map(l => (
                                    <div key={l.id} className="p-8 bg-slate-50 rounded-3xl border border-slate-100 shadow-sm relative group">
                                        <div className="flex justify-between items-center mb-4">
                                          <div className="px-4 py-1.5 bg-white rounded-xl text-xs font-black text-blue-500 shadow-sm">{l.date}</div>
                                          <button onClick={() => deleteDoc(doc(db, 'artifacts', appId, 'public', 'data', `logs_${siteId}`, l.id))} className="text-slate-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"><Trash2 size={18}/></button>
                                        </div>
                                        <div className="font-bold text-xl text-slate-800 leading-relaxed whitespace-pre-wrap">{l.content}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                    
                    <button onClick={handleSave} className="w-full py-8 bg-slate-950 text-white rounded-[32px] font-black text-3xl shadow-2xl active:scale-95 hover:bg-black transition-all mt-12 flex items-center justify-center gap-3">
                      <Save size={32} /> 최종 데이터 저장
                    </button>
                </div>
            </div>
        </div>
    );
};

// --- [보조 UI 유틸리티] ---
const MobileInput = ({ label, value, onChange, placeholder }) => (
    <div className="space-y-3">
        <label className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] ml-2">{label}</label>
        <input className="w-full p-6 bg-slate-50 rounded-[24px] border border-slate-100 outline-none focus:ring-4 ring-blue-100 focus:bg-white transition-all font-bold text-2xl" value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} />
    </div>
);

const MetricCard = ({ title, count, color, onClick }) => (
    <button onClick={onClick} className="bg-white p-10 rounded-[45px] border border-slate-200 shadow-xl flex items-center justify-between group active:scale-95 transition-all w-full relative overflow-hidden">
        <div className={`absolute top-0 right-0 w-32 h-32 ${color === 'blue' ? 'bg-blue-500/5' : 'bg-orange-500/5'} rounded-full -mr-16 -mt-16`} />
        <div className="text-left z-10">
            <p className="text-sm font-black text-slate-400 uppercase tracking-widest mb-3">{title}</p>
            <p className={`text-7xl font-black ${color === 'blue' ? 'text-blue-600' : 'text-orange-500'} tracking-tighter`}>{count}<span className="text-2xl ml-2 text-slate-300 font-bold">건</span></p>
        </div>
        <div className={`p-8 rounded-[35px] z-10 ${color === 'blue' ? 'bg-blue-50 text-blue-600' : 'bg-orange-50 text-orange-600'} group-hover:rotate-12 transition-transform shadow-sm`}><ArrowRight size={48}/></div>
  </button>
);

const LinkModal = ({ link, onClose, onSave, onDelete }) => {
  const [title, setTitle] = useState(link?.title || '');
  const [url, setUrl] = useState(link?.url || '');
  return (
    <div className="fixed inset-0 z-[300] flex items-center justify-center bg-black/95 backdrop-blur-xl p-6">
       <div className="bg-white w-full max-w-lg rounded-[50px] p-12 space-y-10 shadow-2xl">
          <div className="flex justify-between items-center">
            <h3 className="text-3xl font-black tracking-tighter">바로가기 설정</h3>
            <button onClick={onClose} className="text-slate-300 hover:text-slate-900"><X size={32}/></button>
          </div>
          <div className="space-y-6">
            <div className="space-y-2">
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] ml-2">아이콘 제목</span>
              <input className="w-full p-6 bg-slate-50 rounded-3xl outline-none font-black text-2xl border border-slate-100" placeholder="제목" value={title} onChange={e => setTitle(e.target.value)} />
            </div>
            <div className="space-y-2">
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] ml-2">이동 URL</span>
              <input className="w-full p-6 bg-slate-50 rounded-3xl outline-none font-mono text-lg border border-slate-100" placeholder="https://..." value={url} onChange={e => setUrl(e.target.value)} />
            </div>
          </div>
          <div className="flex flex-col gap-4 pt-4">
            <button onClick={() => onSave(title, url)} className="w-full p-6 bg-blue-600 text-white rounded-3xl font-black text-xl shadow-xl hover:bg-blue-700 transition-all">설정 저장하기</button>
            {link && <button onClick={() => onDelete(link.id)} className="w-full p-4 text-red-500 font-bold text-sm underline decoration-2 underline-offset-4">항목 삭제</button>}
            <button onClick={onClose} className="w-full p-4 font-black text-slate-400">닫기</button>
          </div>
       </div>
    </div>
  );
};

export default App;
