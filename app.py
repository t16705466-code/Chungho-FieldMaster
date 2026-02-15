
import React, { useState, useEffect, useRef } from 'react';
import { 
  ChevronLeft, Save, Plus, Trash2, FileText, Camera, 
  Calculator, StickyNote, Users, Search, Filter, ArrowRight,
  ExternalLink, Calendar, LayoutDashboard, Settings, PlusCircle, Link2, X, Edit2, List, ClipboardList, Loader2
} from 'lucide-react';
// Firebase 관련 임포트
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, collection, doc, setDoc, onSnapshot, query, addDoc, updateDoc, deleteDoc } from 'firebase/firestore';
// Firebase 설정 (환경 변수 자동 연결)
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'work-log-pro-system';
const App = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('dashboard'); // 'dashboard' or 'detail'
  const [activeTab, setActiveTab] = useState('home'); // 'home', 'progress', 'quote', 'all'
  const [masterData, setMasterData] = useState([]);
  const [quickLinks, setQuickLinks] = useState([]);
  const [isLinkModalOpen, setIsLinkModalOpen] = useState(false);
  const [editingLink, setEditingLink] = useState(null);
  const [currentDetail, setCurrentDetail] = useState(null);
  // 1. 구글 클라우드(Firebase) 인증
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (error) {
        console.error("인증 오류:", error);
      }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);
  // 2. 실시간 데이터 동기화 리스너
  useEffect(() => {
    if (!user) return;
    // 현장 마스터 DB 리스너
    const masterRef = collection(db, 'artifacts', appId, 'public', 'data', 'masterData');
    const unsubMaster = onSnapshot(masterRef, (snapshot) => {
      const data = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setMasterData(data);
    }, (error) => console.error("데이터 수신 오류:", error));
    // 바로가기 리스너
    const linksRef = collection(db, 'artifacts', appId, 'public', 'data', 'quickLinks');
    const unsubLinks = onSnapshot(linksRef, (snapshot) => {
      const data = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setQuickLinks(data);
    }, (error) => console.error("링크 수신 오류:", error));
    return () => { unsubMaster(); unsubLinks(); };
  }, [user]);
  // --- 핸들러 ---
  const handleRowClick = (item) => {
    setCurrentDetail(item);
    setView('detail');
  };
  const handleCreateNew = () => {
    setCurrentDetail({
      manageNo: '',
      jurisdiction: '',
      siteName: '',
      bizAddress: '',
      siteAddress: '',
      memo: '',
      contractAmount: '',
      advancePayment: '',
      intermediatePayment: '',
    });
    setView('detail');
  };
  const handleSaveMaster = async (updatedData) => {
    if (!user) return;
    try {
      const collectionRef = collection(db, 'artifacts', appId, 'public', 'data', 'masterData');
      if (updatedData.id) {
        await setDoc(doc(collectionRef, updatedData.id), updatedData, { merge: true });
      } else {
        await addDoc(collectionRef, { ...updatedData, createdAt: new Date() });
      }
      setView('dashboard');
    } catch (err) {
      console.error("저장 오류:", err);
    }
  };
  const navigateToTab = (tab) => {
    setActiveTab(tab);
    setView('dashboard');
  };
  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-900 text-white">
        <Loader2 className="animate-spin mb-4 text-blue-500" size={64} />
        <p className="font-black text-2xl tracking-tighter">데이터 클라우드 연결 중...</p>
      </div>
    );
  }
  return (
    <div className="min-h-screen bg-[#f1f5f9] font-sans text-slate-900 flex flex-col relative">
      
      {/* 상단 헤더 (로고 및 네비게이션) */}
      <header className="bg-slate-950 border-b border-slate-800 sticky top-0 z-[100] shadow-2xl">
        <div className="max-w-[1800px] mx-auto px-4 sm:px-8 h-16 sm:h-20 flex items-center justify-between">
          <div className="flex items-center gap-6 sm:gap-10">
            {/* 로고: 업무일지 */}
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigateToTab('home')}>
              <div className="bg-blue-600 p-2 rounded-xl text-white shadow-[0_0_20px_rgba(37,99,235,0.4)]">
                <ClipboardList size={26} />
              </div>
              <span className="text-xl sm:text-2xl font-black tracking-tighter text-white">업무일지</span>
            </div>
            
            {/* 메인 메뉴 */}
            <nav className="hidden lg:flex items-center gap-2">
              <NavButton active={view === 'dashboard' && activeTab === 'home'} onClick={() => navigateToTab('home')} icon={<LayoutDashboard size={18}/>} label="대시보드" />
              <NavButton active={view === 'dashboard' && activeTab === 'progress'} onClick={() => navigateToTab('progress')} icon={<ArrowRight size={18} className="text-blue-400"/>} label="진행중 리스트" />
              <NavButton active={view === 'dashboard' && activeTab === 'quote'} onClick={() => navigateToTab('quote')} icon={<ArrowRight size={18} className="text-orange-400"/>} label="견적중 리스트" />
              <div className="w-px h-8 bg-slate-800 mx-3" />
              <NavButton active={view === 'dashboard' && activeTab === 'all'} onClick={() => navigateToTab('all')} icon={<List size={18}/>} label="데이터베이스" />
              <NavButton active={view === 'detail' && !currentDetail?.id} onClick={handleCreateNew} icon={<PlusCircle size={18} className="text-emerald-400"/>} label="신규 현장 등록" />
            </nav>
          </div>
          <div className="flex items-center gap-3">
             {/* 모바일 메뉴 전용 아이콘 */}
             <div className="lg:hidden flex gap-2">
               <button onClick={() => navigateToTab('home')} className={`p-2 rounded-lg ${activeTab === 'home' ? 'text-white bg-slate-800' : 'text-slate-400'}`}><LayoutDashboard size={22}/></button>
               <button onClick={() => navigateToTab('all')} className={`p-2 rounded-lg ${activeTab === 'all' ? 'text-white bg-slate-800' : 'text-slate-400'}`}><List size={22}/></button>
               <button onClick={handleCreateNew} className="p-2 text-emerald-400"><PlusCircle size={22}/></button>
             </div>
             <div className="w-px h-6 bg-slate-800 mx-2 hidden sm:block" />
             <Settings size={22} className="text-slate-500 hover:text-white cursor-pointer transition-colors" />
          </div>
        </div>
      </header>
      {/* 메인 화면 */}
      <div className="flex-1 overflow-y-auto">
        {view === 'dashboard' ? (
          <DashboardView 
            data={masterData} 
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            quickLinks={quickLinks}
            onRowClick={handleRowClick} 
            onAddLink={() => { setEditingLink(null); setIsLinkModalOpen(true); }}
            onEditLink={(link) => { setEditingLink(link); setIsLinkModalOpen(true); }}
          />
        ) : (
          <DetailView 
            data={currentDetail} 
            onBack={() => setView('dashboard')} 
            onSave={handleSaveMaster}
          />
        )}
      </div>
      {/* 링크 관리 모달 */}
      {isLinkModalOpen && (
        <LinkEditModal 
          link={editingLink} 
          onSave={async (title, url) => {
            const ref = collection(db, 'artifacts', appId, 'public', 'data', 'quickLinks');
            if (editingLink) {
              await updateDoc(doc(ref, editingLink.id), { title, url });
            } else {
              await addDoc(ref, { title, url, createdAt: new Date() });
            }
            setIsLinkModalOpen(false);
          }}
          onDelete={async (id) => { 
            await deleteDoc(doc(db, 'artifacts', appId, 'public', 'data', 'quickLinks', id));
            setIsLinkModalOpen(false); 
          }}
          onClose={() => { setIsLinkModalOpen(false); setEditingLink(null); }} 
        />
      )}
    </div>
  );
};
// --- [네비게이션 버튼] ---
const NavButton = ({ active, onClick, icon, label }) => (
  <button 
    onClick={onClick}
    className={`flex items-center gap-2 px-5 py-2.5 rounded-2xl text-sm font-black transition-all ${
      active 
        ? 'bg-slate-800 text-white border border-slate-700 shadow-lg' 
        : 'text-slate-400 hover:bg-slate-900 hover:text-white'
    }`}
  >
    {icon}
    {label}
  </button>
);
// --- [대시보드 뷰 컴포넌트] ---
const DashboardView = ({ data, activeTab, setActiveTab, quickLinks, onRowClick, onAddLink, onEditLink }) => {
  const getStatus = (no) => {
    if (!no) return '-';
    const cleanNo = String(no).replace(/-/g, '');
    return cleanNo.length >= 6 ? '견적중' : '진행중';
  };
  const inProgressList = data.filter(item => getStatus(item.manageNo) === '진행중');
  const quotationList = data.filter(item => getStatus(item.manageNo) === '견적중');
  const calendarEmbedUrl = "https://calendar.google.com/calendar/embed?src=t16705466%40gmail.com&ctz=Asia%2FSeoul";
  // CASE 1: 대시보드 홈 (리스트 없음)
  if (activeTab === 'home') {
    return (
      <div className="max-w-[1800px] mx-auto p-4 sm:p-8 space-y-8 animate-in fade-in duration-500">
        {/* 요약 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SummaryCard title="진행중인 현장" count={inProgressList.length} color="blue" onClick={() => setActiveTab('progress')} />
          <SummaryCard title="견적중인 현장" count={quotationList.length} color="orange" onClick={() => setActiveTab('quote')} />
        </div>
        {/* 바로가기 */}
        <div className="bg-white rounded-[40px] p-8 sm:p-12 border border-slate-200 shadow-xl">
          <div className="flex justify-between items-center mb-8">
            <h3 className="font-black text-slate-800 text-2xl flex items-center gap-4"><Link2 size={28} className="text-blue-600" /> 빠른 바로가기</h3>
            <button onClick={onAddLink} className="bg-slate-100 p-3 rounded-full text-slate-400 hover:text-blue-600 transition-all shadow-sm"><PlusCircle size={28} /></button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-5">
            {quickLinks.slice(0, 10).map(link => (
              <div key={link.id} className="relative group">
                <a href={link.url} target="_blank" rel="noopener noreferrer" className="block p-6 bg-slate-50 border border-slate-200 rounded-[32px] text-sm font-black text-slate-700 hover:bg-white hover:border-blue-500 hover:text-blue-600 hover:shadow-2xl transition-all truncate text-center">
                  {link.title}
                </a>
                <button onClick={(e) => { e.preventDefault(); onEditLink(link); }} className="absolute right-3 top-3 p-2 bg-white border border-slate-200 rounded-full text-slate-300 hover:text-blue-500 opacity-0 lg:group-hover:opacity-100 transition-opacity shadow-sm"><Edit2 size={12} /></button>
              </div>
            ))}
            {quickLinks.length < 10 && (
              <button onClick={onAddLink} className="p-6 border-2 border-dashed border-slate-200 rounded-[32px] text-sm font-black text-slate-400 flex items-center justify-center gap-3 hover:border-blue-400 hover:text-blue-500 transition-all"><Plus size={20} /> 추가</button>
            )}
          </div>
        </div>
        {/* 캘린더 */}
        <section className="bg-white rounded-[40px] border border-slate-200 shadow-2xl overflow-hidden">
          <div className="p-10 border-b border-slate-100 flex items-center gap-4 bg-slate-50/30">
            <Calendar size={32} className="text-red-500" />
            <h3 className="font-black text-slate-800 text-2xl tracking-tight">구글 업무 일정 캘린더</h3>
          </div>
          <div className="p-6 sm:p-10 h-[800px] bg-slate-50">
             <iframe src={calendarEmbedUrl} style={{ border: 0 }} width="100%" height="100%" frameBorder="0" scrolling="no" title="Google Calendar" className="rounded-[40px] border border-slate-200 shadow-2xl bg-white" />
          </div>
        </section>
      </div>
    );
  }
  // CASE 2: 리스트 전용 뷰 (대시보드 요소 없음)
  const displayList = activeTab === 'progress' ? inProgressList : activeTab === 'quote' ? quotationList : data;
  
  return (
    <div className="max-w-[1800px] mx-auto p-4 sm:p-8 animate-in fade-in duration-300">
      <div className="bg-white rounded-[50px] border border-slate-200 shadow-2xl overflow-hidden flex flex-col min-h-[800px]">
        <div className="p-10 sm:p-14 border-b border-slate-100 flex flex-col xl:flex-row justify-between xl:items-center gap-8 bg-slate-50/50">
          <div className="flex items-center gap-5">
            <div className={`p-4 rounded-3xl text-white ${activeTab === 'quote' ? 'bg-orange-500' : activeTab === 'progress' ? 'bg-blue-600' : 'bg-slate-800'}`}>
               <List size={32} />
            </div>
            <div>
              <h3 className="font-black text-slate-900 text-4xl tracking-tighter">
                {activeTab === 'progress' ? '진행중 현장' : activeTab === 'quote' ? '견적중 현장' : '마스터 데이터베이스'}
              </h3>
              <p className="text-slate-400 font-bold mt-1 uppercase tracking-widest text-sm">Total {displayList.length} sites registered</p>
            </div>
          </div>
          <div className="relative w-full xl:w-[500px]">
            <Search className="absolute left-6 top-5 text-slate-400" size={24} />
            <input type="text" placeholder="현장명, 주소, 관리번호로 검색..." className="w-full pl-16 pr-8 py-5 bg-white border border-slate-200 rounded-[32px] text-xl focus:outline-none focus:ring-4 focus:ring-blue-100 shadow-inner font-medium" />
          </div>
        </div>
        <div className="overflow-auto flex-1">
          <ProjectTable list={displayList} onRowClick={onRowClick} themeColor={activeTab === 'quote' ? 'orange' : 'blue'} />
        </div>
      </div>
    </div>
  );
};
// --- [보조 UI 유틸] ---
const SummaryCard = ({ title, count, color, onClick }) => (
  <button onClick={onClick} className={`w-full bg-white p-10 sm:p-14 rounded-[50px] border ${color === 'blue' ? 'border-blue-100' : 'border-orange-100'} shadow-2xl flex items-center justify-between group hover:scale-[1.03] transition-all`}>
    <div className="text-left">
      <p className="text-sm sm:text-lg font-black text-slate-400 mb-3 uppercase tracking-[0.2em]">{title}</p>
      <p className={`text-6xl sm:text-8xl font-black tracking-tighter leading-none ${color === 'blue' ? 'text-blue-600' : 'text-orange-600'}`}>{count}<span className="text-2xl sm:text-3xl font-bold text-slate-400 ml-4">건</span></p>
    </div>
    <div className={`${color === 'blue' ? 'bg-blue-50 text-blue-600' : 'bg-orange-50 text-orange-600'} p-8 sm:p-12 rounded-[40px] group-hover:rotate-12 transition-transform shadow-xl`}><ArrowRight size={56} /></div>
  </button>
);
const ProjectTable = ({ list, onRowClick, themeColor }) => {
  const formatNum = (num) => parseInt(String(num || '0').replace(/,/g, '')).toLocaleString();
  return (
    <table className="w-full border-collapse text-left min-w-[1800px]">
      <thead className="sticky top-0 z-20">
        <tr className={`${themeColor === 'blue' ? 'bg-slate-900' : 'bg-orange-600'} text-white text-[15px] font-black uppercase tracking-widest`}>
          <th className="p-8 border-r border-white/10 w-40">관리번호</th>
          <th className="p-8 border-r border-white/10 w-32 text-center">관할</th>
          <th className="p-8 border-r border-white/10 w-[500px]">현장명</th>
          <th className="p-8 border-r border-white/10 w-[600px]">주소</th>
          <th className="p-8 border-r border-white/10 w-56 text-right">계약금액</th>
          <th className="p-8 border-r border-white/10 w-56 text-right">총액(VAT)</th>
          <th className="p-8 border-r border-white/10 w-56 text-right text-emerald-300">수금액</th>
          <th className="p-8 border-r border-white/10 w-56 text-right text-yellow-300">잔금</th>
          <th className="p-8">특이사항</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-100 bg-white">
        {list.map(item => {
          const cAmt = parseInt(String(item.contractAmount || '0').replace(/,/g, '')) || 0;
          const paid = (parseInt(String(item.advancePayment || '0').replace(/,/g, '')) || 0) + (parseInt(String(item.intermediatePayment || '0').replace(/,/g, '')) || 0);
          const total = cAmt + Math.floor(cAmt * 0.1);
          return (
            <tr key={item.id} onClick={() => onRowClick(item)} className="group cursor-pointer hover:bg-slate-50 transition-all">
              <td className="p-8 font-black text-slate-800 text-lg border-r border-slate-100">{item.manageNo}</td>
              <td className="p-8 font-bold text-slate-400 text-center border-r border-slate-100">{item.jurisdiction}</td>
              <td className="p-8 font-black text-slate-900 text-2xl border-r border-slate-100 group-hover:text-blue-600 transition-colors">{item.siteName}</td>
              <td className="p-8 text-base text-slate-500 font-medium leading-relaxed border-r border-slate-100">{item.siteAddress || item.bizAddress}</td>
              <td className="p-8 text-right font-mono text-xl text-slate-600 border-r border-slate-100">{formatNum(cAmt)}</td>
              <td className="p-8 text-right font-mono font-black text-2xl bg-slate-50/30 border-r border-slate-100 text-slate-800">{formatNum(total)}</td>
              <td className="p-8 text-right font-mono text-xl text-emerald-600 font-black border-r border-slate-100">{formatNum(paid)}</td>
              <td className="p-8 text-right font-mono font-black text-3xl text-red-600 bg-red-50/10">{formatNum(total - paid)}</td>
              <td className="p-8 text-base text-slate-400 italic truncate max-w-[300px]">{item.memo}</td>
            </tr>
          );
        })}
        {list.length === 0 && (
          <tr><td colSpan="9" className="p-80 text-center text-slate-200 font-black text-6xl tracking-widest">NO DATA</td></tr>
        )}
      </tbody>
    </table>
  );
};
const DetailView = ({ data, onBack, onSave }) => {
  const [formData, setFormData] = useState(data);
  const [siteContacts, setSiteContacts] = useState([]);
  const [consultationLogs, setConsultationLogs] = useState([]);
  const activeSiteId = data.id || null;
  // 클라우드에서 관계인 및 상담 일지 실시간 동기화
  useEffect(() => {
    if (!activeSiteId) return;
    const cRef = collection(db, 'artifacts', appId, 'public', 'data', `contacts_${activeSiteId}`);
    const unsubC = onSnapshot(cRef, (s) => setSiteContacts(s.docs.map(d => ({ id: d.id, ...d.data() }))));
    
    const lRef = collection(db, 'artifacts', appId, 'public', 'data', `logs_${activeSiteId}`);
    const unsubL = onSnapshot(lRef, (s) => setConsultationLogs(s.docs.map(d => ({ id: d.id, ...d.data() }))));
    return () => { unsubC(); unsubL(); };
  }, [activeSiteId]);
  const contractAmt = parseInt(String(formData.contractAmount || '0').replace(/,/g, '')) || 0;
  const advPay = parseInt(String(formData.advancePayment || '0').replace(/,/g, '')) || 0;
  const interPay = parseInt(String(formData.intermediatePayment || '0').replace(/,/g, '')) || 0;
  const total = contractAmt + Math.floor(contractAmt * 0.1);
  const balance = total - advPay - interPay;
  const handleFormChange = (field, value) => {
    if (['contractAmount', 'advancePayment', 'intermediatePayment'].includes(field)) {
      setFormData(prev => ({ ...prev, [field]: value.replace(/[^0-9]/g, '') }));
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }
  };
  const updateSub = async (type, sub) => {
    if (!activeSiteId) return alert("현장 기본 정보를 먼저 저장해 주세요.");
    const path = type === 'contact' ? `contacts_${activeSiteId}` : `logs_${activeSiteId}`;
    const ref = collection(db, 'artifacts', appId, 'public', 'data', path);
    if (sub.id) await setDoc(doc(ref, sub.id), sub);
    else await addDoc(ref, { ...sub, createdAt: new Date() });
  };
  return (
    <div className="max-w-[1600px] mx-auto p-6 animate-in fade-in slide-in-from-bottom-10 pb-40 space-y-16">
      <div className="bg-white rounded-[70px] shadow-2xl overflow-hidden border border-slate-200">
        <div className="p-12 sm:p-20 border-b border-slate-100 bg-slate-900 flex flex-col lg:flex-row justify-between items-center gap-10">
          <div className="space-y-6 text-center lg:text-left">
            <button onClick={onBack} className="flex items-center gap-3 text-slate-400 hover:text-white font-black text-sm uppercase tracking-widest mx-auto lg:mx-0 transition-colors"><ChevronLeft size={24} /> BACK TO LIST</button>
            <h1 className="text-5xl sm:text-8xl font-black text-white tracking-tighter leading-none">
              {formData.siteName || 'NEW PROJECT'} <br/>
              <span className="text-blue-500 font-mono text-3xl sm:text-5xl opacity-90 mt-6 block tracking-normal">[{formData.manageNo || 'ID-WAITING'}]</span>
            </h1>
          </div>
          <div className="flex gap-6 shrink-0 scale-110 sm:scale-125">
            <StatusBadge label="STATUS" value={formData.manageNo.replace(/-/g, '').length >= 6 ? '견적중' : '진행중'} color={formData.manageNo.replace(/-/g, '').length >= 6 ? 'orange' : 'blue'} />
            <StatusBadge label="BALANCE" value={`${balance.toLocaleString()}원`} color="red" />
          </div>
        </div>
        <div className="p-10 sm:p-20 space-y-24">
          <section>
            <h2 className="text-4xl font-black mb-12 text-slate-900 flex items-center gap-5"><div className="w-5 h-14 bg-blue-600 rounded-full" /> 현장 개요 정보</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0 border border-slate-200 rounded-[56px] overflow-hidden shadow-2xl bg-white">
              <InputBox label="관리번호" value={formData.manageNo} onChange={(v) => handleFormChange('manageNo', v)} />
              <DisplayBox label="현재 진행 상태" value={formData.manageNo.replace(/-/g, '').length >= 6 ? '견적중' : '진행중'} color="text-blue-700" />
              <InputBox label="관할서" value={formData.jurisdiction} onChange={(v) => handleFormChange('jurisdiction', v)} />
              <InputBox label="현장명 (회사명)" value={formData.siteName} onChange={(v) => handleFormChange('siteName', v)} fullWidth />
              <InputBox label="사업장 주소" value={formData.bizAddress} onChange={(v) => handleFormChange('bizAddress', v)} fullWidth />
              <InputBox label="실제 현장 주소" value={formData.siteAddress} onChange={(v) => handleFormChange('siteAddress', v)} fullWidth />
              <InputBox label="현장 메모장" value={formData.memo} onChange={(v) => handleFormChange('memo', v)} fullWidth multiline />
            </div>
          </section>
          <section>
            <h2 className="text-4xl font-black mb-12 text-slate-900 flex items-center gap-5"><div className="w-5 h-14 bg-emerald-500 rounded-full" /> 금전 및 수금 관리</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0 border border-slate-200 rounded-[56px] overflow-hidden shadow-2xl bg-white">
              <InputBox label="계약금액 (공급가)" value={contractAmt.toLocaleString()} onChange={(v) => handleFormChange('contractAmount', v)} highlight />
              <DisplayBox label="부가세 (10%)" value={(contractAmt * 0.1).toLocaleString()} />
              <DisplayBox label="총액 (VAT포함)" value={total.toLocaleString()} bg="bg-blue-50/50" color="text-blue-800" />
              <InputBox label="선수금" value={advPay.toLocaleString()} onChange={(v) => handleFormChange('advancePayment', v)} />
              <InputBox label="중도금" value={interPay.toLocaleString()} onChange={(v) => handleFormChange('intermediatePayment', v)} />
              <DisplayBox label="미수금 (최종 잔금)" value={balance.toLocaleString()} bg="bg-red-50/50" color="text-red-700" />
            </div>
          </section>
          {activeSiteId ? (
            <>
              {/* 관계인 정보 */}
              <section>
                <div className="flex justify-between items-end mb-12 px-6">
                  <h2 className="text-4xl font-black text-slate-900 flex items-center gap-5"><div className="w-5 h-14 bg-indigo-500 rounded-full" /> 현장 관계인 관리</h2>
                  <button onClick={() => updateSub('contact', { company: '', name: '', position: '', mobile: '' })} className="px-10 py-5 bg-indigo-700 text-white rounded-[32px] font-black flex items-center gap-4 shadow-2xl transition-all hover:scale-105 active:scale-95"><Plus size={28} /> 관계인 추가</button>
                </div>
                <div className="overflow-x-auto border border-slate-200 rounded-[56px] shadow-2xl bg-white">
                  <table className="w-full border-collapse min-w-[1200px]">
                    <thead className="bg-indigo-700 text-white uppercase text-sm">
                      <tr><th className="p-6 border-r border-indigo-600/50">회사명</th><th className="p-6 border-r border-indigo-600/50 w-44">이름</th><th className="p-6 border-r border-indigo-600/50 w-44">직위</th><th className="p-6 border-r border-indigo-600/50">모바일</th><th className="p-6">이메일/비고</th><th className="p-6 w-20 bg-white"></th></tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-bold text-lg">
                      {siteContacts.map(c => (
                        <tr key={c.id} className="hover:bg-indigo-50/30 transition-colors">
                          <td className="p-0 border-r border-slate-100"><input type="text" className="w-full p-6 outline-none font-bold" value={c.company} onChange={e => updateSub('contact', {...c, company: e.target.value})} /></td>
                          <td className="p-0 border-r border-slate-100"><input type="text" className="w-full p-6 outline-none text-center" value={c.name} onChange={e => updateSub('contact', {...c, name: e.target.value})} /></td>
                          <td className="p-0 border-r border-slate-100"><input type="text" className="w-full p-6 outline-none text-center" value={c.position} onChange={e => updateSub('contact', {...c, position: e.target.value})} /></td>
                          <td className="p-0 border-r border-slate-100"><input type="text" className="w-full p-6 outline-none text-center text-blue-600 font-mono" value={c.mobile} onChange={e => updateSub('contact', {...c, mobile: e.target.value})} /></td>
                          <td className="p-0"><input type="text" className="w-full p-6 outline-none" value={c.note || ''} onChange={e => updateSub('contact', {...c, note: e.target.value})} /></td>
                          <td className="p-6 text-center"><button onClick={async () => await deleteDoc(doc(db, 'artifacts', appId, 'public', 'data', `contacts_${activeSiteId}`, c.id))} className="text-slate-200 hover:text-red-500 transition-colors"><Trash2 size={28}/></button></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
              {/* 상담 일지 */}
              <section>
                <div className="flex justify-between items-end mb-12 px-6">
                  <h2 className="text-4xl font-black text-slate-900 flex items-center gap-5"><div className="w-5 h-14 bg-cyan-600 rounded-full" /> 상세 상담 및 업무 기록</h2>
                  <button onClick={() => updateSub('log', { date: new Date().toISOString().split('T')[0], type: '', content: '' })} className="px-10 py-5 bg-cyan-700 text-white rounded-[32px] font-black flex items-center gap-4 shadow-2xl transition-all hover:scale-105 active:scale-95"><Plus size={28} /> 일지 작성</button>
                </div>
                <div className="overflow-x-auto border border-slate-200 rounded-[56px] shadow-2xl bg-white">
                  <table className="w-full border-collapse min-w-[1200px] font-bold text-lg">
                    <thead className="bg-cyan-700 text-white uppercase text-sm">
                      <tr><th className="p-6 border-r border-cyan-600/50 w-56 text-center">상담일</th><th className="p-6 border-r border-cyan-600/50 w-64">업무형태</th><th className="p-6 border-r border-cyan-600/50">내용</th><th className="p-6 w-20 bg-white"></th></tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {consultationLogs.map(l => (
                        <tr key={l.id} className="hover:bg-cyan-50/30 transition-colors">
                          <td className="p-0 border-r border-slate-100"><input type="date" className="w-full p-6 outline-none font-bold text-center text-xl" value={l.date} onChange={e => updateSub('log', {...l, date: e.target.value})} /></td>
                          <td className="p-0 border-r border-slate-100"><input type="text" className="w-full p-6 outline-none font-bold text-center" placeholder="..." value={l.type} onChange={e => updateSub('log', {...l, type: e.target.value})} /></td>
                          <td className="p-0 border-r border-slate-100"><textarea rows="1" className="w-full p-6 outline-none font-bold resize-none overflow-hidden leading-relaxed" value={l.content} onChange={e => updateSub('log', {...l, content: e.target.value})} onInput={e => {e.target.style.height = 'auto'; e.target.style.height = e.target.scrollHeight + 'px';}} /></td>
                          <td className="p-6 text-center"><button onClick={async () => await deleteDoc(doc(db, 'artifacts', appId, 'public', 'data', `logs_${activeSiteId}`, l.id))} className="text-slate-200 hover:text-red-500 transition-colors"><Trash2 size={28}/></button></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </>
          ) : (
            <div className="p-40 bg-slate-50 rounded-[70px] border-4 border-dashed border-slate-200 text-center text-slate-300 font-black text-4xl">먼저 기본 정보를 저장하여 관리 번호를 등록해 주세요.</div>
          )}
          <div className="flex justify-center pt-20"><button onClick={() => onSave(formData)} className="px-60 py-12 bg-slate-950 text-white rounded-[40px] hover:bg-black hover:scale-105 transition-all shadow-[0_50px_100px_rgba(0,0,0,0.5)] font-black text-5xl active:scale-95">최종 데이터 저장</button></div>
        </div>
      </div>
    </div>
  );
};
// --- [공통 UI 박스] ---
const InputBox = ({ label, value, onChange, fullWidth = false, highlight = false, multiline = false }) => {
  const ref = useRef(null);
  useEffect(() => { if (multiline && ref.current) { ref.current.style.height = 'auto'; ref.current.style.height = ref.current.scrollHeight + 'px'; } }, [value, multiline]);
  return (
    <div className={`flex flex-col border-b border-r border-slate-100 py-10 px-14 group hover:bg-slate-50 transition-colors ${fullWidth ? 'md:col-span-2 lg:col-span-3 border-r-0' : ''}`}>
      <label className="text-[16px] font-black text-slate-400 uppercase mb-4 group-focus-within:text-blue-600 tracking-[0.2em] leading-none">{label}</label>
      {multiline ? <textarea ref={ref} className="bg-transparent outline-none border-none p-0 text-3xl font-black resize-none overflow-hidden text-slate-800 leading-tight" value={value} onChange={(e) => onChange(e.target.value)} rows={1} /> : <input type="text" className={`bg-transparent outline-none border-none p-0 text-3xl font-black ${highlight ? 'text-blue-800' : 'text-slate-900'}`} value={value} onChange={(e) => onChange(e.target.value)} />}
    </div>
  );
};
const DisplayBox = ({ label, value, color = "text-slate-700", bg = "bg-white" }) => (
  <div className={`flex flex-col border-b border-r border-slate-100 py-10 px-14 ${bg}`}>
    <span className="text-[16px] font-black text-slate-300 uppercase mb-4 tracking-[0.2em] leading-none">{label}</span>
    <span className={`text-3xl font-black ${color}`}>{value}</span>
  </div>
);
const StatusBadge = ({ label, value, color }) => (
  <div className={`bg-white/10 backdrop-blur-md p-8 rounded-[40px] border border-white/20 text-center min-w-[200px] shadow-2xl`}>
    <p className={`text-[12px] font-black uppercase tracking-[0.3em] mb-2 ${color === 'red' ? 'text-red-400' : 'text-slate-400'}`}>{label}</p>
    <p className={`text-4xl font-black ${color === 'blue' ? 'text-blue-400' : color === 'orange' ? 'text-orange-400' : 'text-red-500'}`}>{value}</p>
  </div>
);
const LinkEditModal = ({ link, onSave, onDelete, onClose }) => {
  const [title, setTitle] = useState(link?.title || '');
  const [url, setUrl] = useState(link?.url || '');
  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/90 backdrop-blur-3xl animate-in fade-in duration-500">
      <div className="bg-white w-full max-w-2xl rounded-[80px] shadow-[0_50px_100px_rgba(0,0,0,0.8)] overflow-hidden">
        <div className="p-14 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h3 className="text-4xl font-black text-slate-900 tracking-tighter leading-none">QUICK LINK</h3>
          <button onClick={onClose} className="p-4 text-slate-300 hover:text-slate-900 transition-colors"><X size={48}/></button>
        </div>
        <div className="p-14 space-y-12">
          <div className="space-y-4">
            <label className="text-[14px] font-black text-slate-400 uppercase tracking-widest ml-3">아이콘 제목</label>
            <input type="text" className="w-full px-10 py-8 bg-slate-100 border-none rounded-[40px] focus:ring-8 focus:ring-blue-100 outline-none font-black text-slate-800 text-3xl" value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="space-y-4">
            <label className="text-[14px] font-black text-slate-400 uppercase tracking-widest ml-3">URL (https://...)</label>
            <input type="text" className="w-full px-10 py-8 bg-slate-100 border-none rounded-[40px] focus:ring-8 focus:ring-blue-100 outline-none font-bold text-slate-600 font-mono text-xl" value={url} onChange={(e) => setUrl(e.target.value)} />
          </div>
        </div>
        <div className="p-14 pt-0 flex justify-between">
          {link ? <button onClick={() => onDelete(link.id)} className="text-red-500 font-black hover:bg-red-50 px-10 py-5 rounded-[30px] text-xl">DELETE</button> : <div />}
          <div className="flex gap-6">
            <button onClick={onClose} className="px-10 py-5 text-slate-400 font-black text-xl hover:text-slate-900">CLOSE</button>
            <button onClick={() => onSave(title, url)} className="px-20 py-6 bg-blue-600 text-white font-black rounded-[40px] hover:bg-blue-700 shadow-2xl text-2xl">SAVE</button>
          </div>
        </div>
      </div>
    </div>
  );
};
export default App;



import React, { useState, useEffect, useRef } from 'react';
import { 
  ChevronLeft, Save, Plus, Trash2, FileText, Camera, 
  Calculator, StickyNote, Users, Search, Filter, ArrowRight,
  ExternalLink, Calendar, LayoutDashboard, Settings, PlusCircle, Link2, X, Edit2, List, ClipboardList, Loader2
} from 'lucide-react';
// Firebase 관련 임포트
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, collection, doc, setDoc, onSnapshot, query, addDoc, updateDoc, deleteDoc } from 'firebase/firestore';
// Firebase 설정 (환경 변수 자동 연결)
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'work-log-pro-system';
const App = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('dashboard'); // 'dashboard' or 'detail'
  const [activeTab, setActiveTab] = useState('home'); // 'home', 'progress', 'quote', 'all'
  const [masterData, setMasterData] = useState([]);
  const [quickLinks, setQuickLinks] = useState([]);
  const [isLinkModalOpen, setIsLinkModalOpen] = useState(false);
  const [editingLink, setEditingLink] = useState(null);
  const [currentDetail, setCurrentDetail] = useState(null);
  // 1. 구글 클라우드(Firebase) 인증
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (error) {
        console.error("인증 오류:", error);
      }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);
  // 2. 실시간 데이터 동기화 리스너
  useEffect(() => {
    if (!user) return;
    // 현장 마스터 DB 리스너
    const masterRef = collection(db, 'artifacts', appId, 'public', 'data', 'masterData');
    const unsubMaster = onSnapshot(masterRef, (snapshot) => {
      const data = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setMasterData(data);
    }, (error) => console.error("데이터 수신 오류:", error));
    // 바로가기 리스너
    const linksRef = collection(db, 'artifacts', appId, 'public', 'data', 'quickLinks');
    const unsubLinks = onSnapshot(linksRef, (snapshot) => {
      const data = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setQuickLinks(data);
    }, (error) => console.error("링크 수신 오류:", error));
    return () => { unsubMaster(); unsubLinks(); };
  }, [user]);
  // --- 핸들러 ---
  const handleRowClick = (item) => {
    setCurrentDetail(item);
    setView('detail');
  };
  const handleCreateNew = () => {
    setCurrentDetail({
      manageNo: '',
      jurisdiction: '',
      siteName: '',
      bizAddress: '',
      siteAddress: '',
      memo: '',
      contractAmount: '',
      advancePayment: '',
      intermediatePayment: '',
    });
    setView('detail');
  };
  const handleSaveMaster = async (updatedData) => {
    if (!user) return;
    try {
      const collectionRef = collection(db, 'artifacts', appId, 'public', 'data', 'masterData');
      if (updatedData.id) {
        await setDoc(doc(collectionRef, updatedData.id), updatedData, { merge: true });
      } else {
        await addDoc(collectionRef, { ...updatedData, createdAt: new Date() });
      }
      setView('dashboard');
    } catch (err) {
      console.error("저장 오류:", err);
    }
  };
  const navigateToTab = (tab) => {
    setActiveTab(tab);
    setView('dashboard');
  };
  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-900 text-white">
        <Loader2 className="animate-spin mb-4 text-blue-500" size={64} />
        <p className="font-black text-2xl tracking-tighter">데이터 클라우드 연결 중...</p>
      </div>
    );
  }
  return (
    <div className="min-h-screen bg-[#f1f5f9] font-sans text-slate-900 flex flex-col relative">
      
      {/* 상단 헤더 (로고 및 네비게이션) */}
      <header className="bg-slate-950 border-b border-slate-800 sticky top-0 z-[100] shadow-2xl">
        <div className="max-w-[1800px] mx-auto px-4 sm:px-8 h-16 sm:h-20 flex items-center justify-between">
          <div className="flex items-center gap-6 sm:gap-10">
            {/* 로고: 업무일지 */}
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigateToTab('home')}>
              <div className="bg-blue-600 p-2 rounded-xl text-white shadow-[0_0_20px_rgba(37,99,235,0.4)]">
                <ClipboardList size={26} />
              </div>
              <span className="text-xl sm:text-2xl font-black tracking-tighter text-white">업무일지</span>
            </div>
            
            {/* 메인 메뉴 */}
            <nav className="hidden lg:flex items-center gap-2">
              <NavButton active={view === 'dashboard' && activeTab === 'home'} onClick={() => navigateToTab('home')} icon={<LayoutDashboard size={18}/>} label="대시보드" />
              <NavButton active={view === 'dashboard' && activeTab === 'progress'} onClick={() => navigateToTab('progress')} icon={<ArrowRight size={18} className="text-blue-400"/>} label="진행중 리스트" />
              <NavButton active={view === 'dashboard' && activeTab === 'quote'} onClick={() => navigateToTab('quote')} icon={<ArrowRight size={18} className="text-orange-400"/>} label="견적중 리스트" />
              <div className="w-px h-8 bg-slate-800 mx-3" />
              <NavButton active={view === 'dashboard' && activeTab === 'all'} onClick={() => navigateToTab('all')} icon={<List size={18}/>} label="데이터베이스" />
              <NavButton active={view === 'detail' && !currentDetail?.id} onClick={handleCreateNew} icon={<PlusCircle size={18} className="text-emerald-400"/>} label="신규 현장 등록" />
            </nav>
          </div>
          <div className="flex items-center gap-3">
             {/* 모바일 메뉴 전용 아이콘 */}
             <div className="lg:hidden flex gap-2">
               <button onClick={() => navigateToTab('home')} className={`p-2 rounded-lg ${activeTab === 'home' ? 'text-white bg-slate-800' : 'text-slate-400'}`}><LayoutDashboard size={22}/></button>
               <button onClick={() => navigateToTab('all')} className={`p-2 rounded-lg ${activeTab === 'all' ? 'text-white bg-slate-800' : 'text-slate-400'}`}><List size={22}/></button>
               <button onClick={handleCreateNew} className="p-2 text-emerald-400"><PlusCircle size={22}/></button>
             </div>
             <div className="w-px h-6 bg-slate-800 mx-2 hidden sm:block" />
             <Settings size={22} className="text-slate-500 hover:text-white cursor-pointer transition-colors" />
          </div>
        </div>
      </header>
      {/* 메인 화면 */}
      <div className="flex-1 overflow-y-auto">
        {view === 'dashboard' ? (
          <DashboardView 
            data={masterData} 
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            quickLinks={quickLinks}
            onRowClick={handleRowClick} 
            onAddLink={() => { setEditingLink(null); setIsLinkModalOpen(true); }}
            onEditLink={(link) => { setEditingLink(link); setIsLinkModalOpen(true); }}
          />
        ) : (
          <DetailView 
            data={currentDetail} 
            onBack={() => setView('dashboard')} 
            onSave={handleSaveMaster}
          />
        )}
      </div>
      {/* 링크 관리 모달 */}
      {isLinkModalOpen && (
        <LinkEditModal 
          link={editingLink} 
          onSave={async (title, url) => {
            const ref = collection(db, 'artifacts', appId, 'public', 'data', 'quickLinks');
            if (editingLink) {
              await updateDoc(doc(ref, editingLink.id), { title, url });
            } else {
              await addDoc(ref, { title, url, createdAt: new Date() });
            }
            setIsLinkModalOpen(false);
          }}
          onDelete={async (id) => { 
            await deleteDoc(doc(db, 'artifacts', appId, 'public', 'data', 'quickLinks', id));
            setIsLinkModalOpen(false); 
          }}
          onClose={() => { setIsLinkModalOpen(false); setEditingLink(null); }} 
        />
      )}
    </div>
  );
};
// --- [네비게이션 버튼] ---
const NavButton = ({ active, onClick, icon, label }) => (
  <button 
    onClick={onClick}
    className={`flex items-center gap-2 px-5 py-2.5 rounded-2xl text-sm font-black transition-all ${
      active 
        ? 'bg-slate-800 text-white border border-slate-700 shadow-lg' 
        : 'text-slate-400 hover:bg-slate-900 hover:text-white'
    }`}
  >
    {icon}
    {label}
  </button>
);
// --- [대시보드 뷰 컴포넌트] ---
const DashboardView = ({ data, activeTab, setActiveTab, quickLinks, onRowClick, onAddLink, onEditLink }) => {
  const getStatus = (no) => {
    if (!no) return '-';
    const cleanNo = String(no).replace(/-/g, '');
    return cleanNo.length >= 6 ? '견적중' : '진행중';
  };
  const inProgressList = data.filter(item => getStatus(item.manageNo) === '진행중');
  const quotationList = data.filter(item => getStatus(item.manageNo) === '견적중');
  const calendarEmbedUrl = "https://calendar.google.com/calendar/embed?src=t16705466%40gmail.com&ctz=Asia%2FSeoul";
  // CASE 1: 대시보드 홈 (리스트 없음)
  if (activeTab === 'home') {
    return (
      <div className="max-w-[1800px] mx-auto p-4 sm:p-8 space-y-8 animate-in fade-in duration-500">
        {/* 요약 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SummaryCard title="진행중인 현장" count={inProgressList.length} color="blue" onClick={() => setActiveTab('progress')} />
          <SummaryCard title="견적중인 현장" count={quotationList.length} color="orange" onClick={() => setActiveTab('quote')} />
        </div>
        {/* 바로가기 */}
        <div className="bg-white rounded-[40px] p-8 sm:p-12 border border-slate-200 shadow-xl">
          <div className="flex justify-between items-center mb-8">
            <h3 className="font-black text-slate-800 text-2xl flex items-center gap-4"><Link2 size={28} className="text-blue-600" /> 빠른 바로가기</h3>
            <button onClick={onAddLink} className="bg-slate-100 p-3 rounded-full text-slate-400 hover:text-blue-600 transition-all shadow-sm"><PlusCircle size={28} /></button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-5">
            {quickLinks.slice(0, 10).map(link => (
              <div key={link.id} className="relative group">
                <a href={link.url} target="_blank" rel="noopener noreferrer" className="block p-6 bg-slate-50 border border-slate-200 rounded-[32px] text-sm font-black text-slate-700 hover:bg-white hover:border-blue-500 hover:text-blue-600 hover:shadow-2xl transition-all truncate text-center">
                  {link.title}
                </a>
                <button onClick={(e) => { e.preventDefault(); onEditLink(link); }} className="absolute right-3 top-3 p-2 bg-white border border-slate-200 rounded-full text-slate-300 hover:text-blue-500 opacity-0 lg:group-hover:opacity-100 transition-opacity shadow-sm"><Edit2 size={12} /></button>
              </div>
            ))}
            {quickLinks.length < 10 && (
              <button onClick={onAddLink} className="p-6 border-2 border-dashed border-slate-200 rounded-[32px] text-sm font-black text-slate-400 flex items-center justify-center gap-3 hover:border-blue-400 hover:text-blue-500 transition-all"><Plus size={20} /> 추가</button>
            )}
          </div>
        </div>
        {/* 캘린더 */}
        <section className="bg-white rounded-[40px] border border-slate-200 shadow-2xl overflow-hidden">
          <div className="p-10 border-b border-slate-100 flex items-center gap-4 bg-slate-50/30">
            <Calendar size={32} className="text-red-500" />
            <h3 className="font-black text-slate-800 text-2xl tracking-tight">구글 업무 일정 캘린더</h3>
          </div>
          <div className="p-6 sm:p-10 h-[800px] bg-slate-50">
             <iframe src={calendarEmbedUrl} style={{ border: 0 }} width="100%" height="100%" frameBorder="0" scrolling="no" title="Google Calendar" className="rounded-[40px] border border-slate-200 shadow-2xl bg-white" />
          </div>
        </section>
      </div>
    );
  }
  // CASE 2: 리스트 전용 뷰 (대시보드 요소 없음)
  const displayList = activeTab === 'progress' ? inProgressList : activeTab === 'quote' ? quotationList : data;
  
  return (
    <div className="max-w-[1800px] mx-auto p-4 sm:p-8 animate-in fade-in duration-300">
      <div className="bg-white rounded-[50px] border border-slate-200 shadow-2xl overflow-hidden flex flex-col min-h-[800px]">
        <div className="p-10 sm:p-14 border-b border-slate-100 flex flex-col xl:flex-row justify-between xl:items-center gap-8 bg-slate-50/50">
          <div className="flex items-center gap-5">
            <div className={`p-4 rounded-3xl text-white ${activeTab === 'quote' ? 'bg-orange-500' : activeTab === 'progress' ? 'bg-blue-600' : 'bg-slate-800'}`}>
               <List size={32} />
            </div>
            <div>
              <h3 className="font-black text-slate-900 text-4xl tracking-tighter">
                {activeTab === 'progress' ? '진행중 현장' : activeTab === 'quote' ? '견적중 현장' : '마스터 데이터베이스'}
              </h3>
              <p className="text-slate-400 font-bold mt-1 uppercase tracking-widest text-sm">Total {displayList.length} sites registered</p>
            </div>
          </div>
          <div className="relative w-full xl:w-[500px]">
            <Search className="absolute left-6 top-5 text-slate-400" size={24} />
            <input type="text" placeholder="현장명, 주소, 관리번호로 검색..." className="w-full pl-16 pr-8 py-5 bg-white border border-slate-200 rounded-[32px] text-xl focus:outline-none focus:ring-4 focus:ring-blue-100 shadow-inner font-medium" />
          </div>
        </div>
        <div className="overflow-auto flex-1">
          <ProjectTable list={displayList} onRowClick={onRowClick} themeColor={activeTab === 'quote' ? 'orange' : 'blue'} />
        </div>
      </div>
    </div>
  );
};
// --- [보조 UI 유틸] ---
const SummaryCard = ({ title, count, color, onClick }) => (
  <button onClick={onClick} className={`w-full bg-white p-10 sm:p-14 rounded-[50px] border ${color === 'blue' ? 'border-blue-100' : 'border-orange-100'} shadow-2xl flex items-center justify-between group hover:scale-[1.03] transition-all`}>
    <div className="text-left">
      <p className="text-sm sm:text-lg font-black text-slate-400 mb-3 uppercase tracking-[0.2em]">{title}</p>
      <p className={`text-6xl sm:text-8xl font-black tracking-tighter leading-none ${color === 'blue' ? 'text-blue-600' : 'text-orange-600'}`}>{count}<span className="text-2xl sm:text-3xl font-bold text-slate-400 ml-4">건</span></p>
    </div>
    <div className={`${color === 'blue' ? 'bg-blue-50 text-blue-600' : 'bg-orange-50 text-orange-600'} p-8 sm:p-12 rounded-[40px] group-hover:rotate-12 transition-transform shadow-xl`}><ArrowRight size={56} /></div>
  </button>
);
const ProjectTable = ({ list, onRowClick, themeColor }) => {
  const formatNum = (num) => parseInt(String(num || '0').replace(/,/g, '')).toLocaleString();
  return (
    <table className="w-full border-collapse text-left min-w-[1800px]">
      <thead className="sticky top-0 z-20">
        <tr className={`${themeColor === 'blue' ? 'bg-slate-900' : 'bg-orange-600'} text-white text-[15px] font-black uppercase tracking-widest`}>
          <th className="p-8 border-r border-white/10 w-40">관리번호</th>
          <th className="p-8 border-r border-white/10 w-32 text-center">관할</th>
          <th className="p-8 border-r border-white/10 w-[500px]">현장명</th>
          <th className="p-8 border-r border-white/10 w-[600px]">주소</th>
          <th className="p-8 border-r border-white/10 w-56 text-right">계약금액</th>
          <th className="p-8 border-r border-white/10 w-56 text-right">총액(VAT)</th>
          <th className="p-8 border-r border-white/10 w-56 text-right text-emerald-300">수금액</th>
          <th className="p-8 border-r border-white/10 w-56 text-right text-yellow-300">잔금</th>
          <th className="p-8">특이사항</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-100 bg-white">
        {list.map(item => {
          const cAmt = parseInt(String(item.contractAmount || '0').replace(/,/g, '')) || 0;
          const paid = (parseInt(String(item.advancePayment || '0').replace(/,/g, '')) || 0) + (parseInt(String(item.intermediatePayment || '0').replace(/,/g, '')) || 0);
          const total = cAmt + Math.floor(cAmt * 0.1);
          return (
            <tr key={item.id} onClick={() => onRowClick(item)} className="group cursor-pointer hover:bg-slate-50 transition-all">
              <td className="p-8 font-black text-slate-800 text-lg border-r border-slate-100">{item.manageNo}</td>
              <td className="p-8 font-bold text-slate-400 text-center border-r border-slate-100">{item.jurisdiction}</td>
              <td className="p-8 font-black text-slate-900 text-2xl border-r border-slate-100 group-hover:text-blue-600 transition-colors">{item.siteName}</td>
              <td className="p-8 text-base text-slate-500 font-medium leading-relaxed border-r border-slate-100">{item.siteAddress || item.bizAddress}</td>
              <td className="p-8 text-right font-mono text-xl text-slate-600 border-r border-slate-100">{formatNum(cAmt)}</td>
              <td className="p-8 text-right font-mono font-black text-2xl bg-slate-50/30 border-r border-slate-100 text-slate-800">{formatNum(total)}</td>
              <td className="p-8 text-right font-mono text-xl text-emerald-600 font-black border-r border-slate-100">{formatNum(paid)}</td>
              <td className="p-8 text-right font-mono font-black text-3xl text-red-600 bg-red-50/10">{formatNum(total - paid)}</td>
              <td className="p-8 text-base text-slate-400 italic truncate max-w-[300px]">{item.memo}</td>
            </tr>
          );
        })}
        {list.length === 0 && (
          <tr><td colSpan="9" className="p-80 text-center text-slate-200 font-black text-6xl tracking-widest">NO DATA</td></tr>
        )}
      </tbody>
    </table>
  );
};
const DetailView = ({ data, onBack, onSave }) => {
  const [formData, setFormData] = useState(data);
  const [siteContacts, setSiteContacts] = useState([]);
  const [consultationLogs, setConsultationLogs] = useState([]);
  const activeSiteId = data.id || null;
  // 클라우드에서 관계인 및 상담 일지 실시간 동기화
  useEffect(() => {
    if (!activeSiteId) return;
    const cRef = collection(db, 'artifacts', appId, 'public', 'data', `contacts_${activeSiteId}`);
    const unsubC = onSnapshot(cRef, (s) => setSiteContacts(s.docs.map(d => ({ id: d.id, ...d.data() }))));
    
    const lRef = collection(db, 'artifacts', appId, 'public', 'data', `logs_${activeSiteId}`);
    const unsubL = onSnapshot(lRef, (s) => setConsultationLogs(s.docs.map(d => ({ id: d.id, ...d.data() }))));
    return () => { unsubC(); unsubL(); };
  }, [activeSiteId]);
  const contractAmt = parseInt(String(formData.contractAmount || '0').replace(/,/g, '')) || 0;
  const advPay = parseInt(String(formData.advancePayment || '0').replace(/,/g, '')) || 0;
  const interPay = parseInt(String(formData.intermediatePayment || '0').replace(/,/g, '')) || 0;
  const total = contractAmt + Math.floor(contractAmt * 0.1);
  const balance = total - advPay - interPay;
  const handleFormChange = (field, value) => {
    if (['contractAmount', 'advancePayment', 'intermediatePayment'].includes(field)) {
      setFormData(prev => ({ ...prev, [field]: value.replace(/[^0-9]/g, '') }));
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }
  };
  const updateSub = async (type, sub) => {
    if (!activeSiteId) return alert("현장 기본 정보를 먼저 저장해 주세요.");
    const path = type === 'contact' ? `contacts_${activeSiteId}` : `logs_${activeSiteId}`;
    const ref = collection(db, 'artifacts', appId, 'public', 'data', path);
    if (sub.id) await setDoc(doc(ref, sub.id), sub);
    else await addDoc(ref, { ...sub, createdAt: new Date() });
  };
  return (
    <div className="max-w-[1600px] mx-auto p-6 animate-in fade-in slide-in-from-bottom-10 pb-40 space-y-16">
      <div className="bg-white rounded-[70px] shadow-2xl overflow-hidden border border-slate-200">
        <div className="p-12 sm:p-20 border-b border-slate-100 bg-slate-900 flex flex-col lg:flex-row justify-between items-center gap-10">
          <div className="space-y-6 text-center lg:text-left">
            <button onClick={onBack} className="flex items-center gap-3 text-slate-400 hover:text-white font-black text-sm uppercase tracking-widest mx-auto lg:mx-0 transition-colors"><ChevronLeft size={24} /> BACK TO LIST</button>
            <h1 className="text-5xl sm:text-8xl font-black text-white tracking-tighter leading-none">
              {formData.siteName || 'NEW PROJECT'} <br/>
              <span className="text-blue-500 font-mono text-3xl sm:text-5xl opacity-90 mt-6 block tracking-normal">[{formData.manageNo || 'ID-WAITING'}]</span>
            </h1>
          </div>
          <div className="flex gap-6 shrink-0 scale-110 sm:scale-125">
            <StatusBadge label="STATUS" value={formData.manageNo.replace(/-/g, '').length >= 6 ? '견적중' : '진행중'} color={formData.manageNo.replace(/-/g, '').length >= 6 ? 'orange' : 'blue'} />
            <StatusBadge label="BALANCE" value={`${balance.toLocaleString()}원`} color="red" />
          </div>
        </div>
        <div className="p-10 sm:p-20 space-y-24">
          <section>
            <h2 className="text-4xl font-black mb-12 text-slate-900 flex items-center gap-5"><div className="w-5 h-14 bg-blue-600 rounded-full" /> 현장 개요 정보</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0 border border-slate-200 rounded-[56px] overflow-hidden shadow-2xl bg-white">
              <InputBox label="관리번호" value={formData.manageNo} onChange={(v) => handleFormChange('manageNo', v)} />
              <DisplayBox label="현재 진행 상태" value={formData.manageNo.replace(/-/g, '').length >= 6 ? '견적중' : '진행중'} color="text-blue-700" />
              <InputBox label="관할서" value={formData.jurisdiction} onChange={(v) => handleFormChange('jurisdiction', v)} />
              <InputBox label="현장명 (회사명)" value={formData.siteName} onChange={(v) => handleFormChange('siteName', v)} fullWidth />
              <InputBox label="사업장 주소" value={formData.bizAddress} onChange={(v) => handleFormChange('bizAddress', v)} fullWidth />
              <InputBox label="실제 현장 주소" value={formData.siteAddress} onChange={(v) => handleFormChange('siteAddress', v)} fullWidth />
              <InputBox label="현장 메모장" value={formData.memo} onChange={(v) => handleFormChange('memo', v)} fullWidth multiline />
            </div>
          </section>
          <section>
            <h2 className="text-4xl font-black mb-12 text-slate-900 flex items-center gap-5"><div className="w-5 h-14 bg-emerald-500 rounded-full" /> 금전 및 수금 관리</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0 border border-slate-200 rounded-[56px] overflow-hidden shadow-2xl bg-white">
              <InputBox label="계약금액 (공급가)" value={contractAmt.toLocaleString()} onChange={(v) => handleFormChange('contractAmount', v)} highlight />
              <DisplayBox label="부가세 (10%)" value={(contractAmt * 0.1).toLocaleString()} />
              <DisplayBox label="총액 (VAT포함)" value={total.toLocaleString()} bg="bg-blue-50/50" color="text-blue-800" />
              <InputBox label="선수금" value={advPay.toLocaleString()} onChange={(v) => handleFormChange('advancePayment', v)} />
              <InputBox label="중도금" value={interPay.toLocaleString()} onChange={(v) => handleFormChange('intermediatePayment', v)} />
              <DisplayBox label="미수금 (최종 잔금)" value={balance.toLocaleString()} bg="bg-red-50/50" color="text-red-700" />
            </div>
          </section>
          {activeSiteId ? (
            <>
              {/* 관계인 정보 */}
              <section>
                <div className="flex justify-between items-end mb-12 px-6">
                  <h2 className="text-4xl font-black text-slate-900 flex items-center gap-5"><div className="w-5 h-14 bg-indigo-500 rounded-full" /> 현장 관계인 관리</h2>
                  <button onClick={() => updateSub('contact', { company: '', name: '', position: '', mobile: '' })} className="px-10 py-5 bg-indigo-700 text-white rounded-[32px] font-black flex items-center gap-4 shadow-2xl transition-all hover:scale-105 active:scale-95"><Plus size={28} /> 관계인 추가</button>
                </div>
                <div className="overflow-x-auto border border-slate-200 rounded-[56px] shadow-2xl bg-white">
                  <table className="w-full border-collapse min-w-[1200px]">
                    <thead className="bg-indigo-700 text-white uppercase text-sm">
                      <tr><th className="p-6 border-r border-indigo-600/50">회사명</th><th className="p-6 border-r border-indigo-600/50 w-44">이름</th><th className="p-6 border-r border-indigo-600/50 w-44">직위</th><th className="p-6 border-r border-indigo-600/50">모바일</th><th className="p-6">이메일/비고</th><th className="p-6 w-20 bg-white"></th></tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-bold text-lg">
                      {siteContacts.map(c => (
                        <tr key={c.id} className="hover:bg-indigo-50/30 transition-colors">
                          <td className="p-0 border-r border-slate-100"><input type="text" className="w-full p-6 outline-none font-bold" value={c.company} onChange={e => updateSub('contact', {...c, company: e.target.value})} /></td>
                          <td className="p-0 border-r border-slate-100"><input type="text" className="w-full p-6 outline-none text-center" value={c.name} onChange={e => updateSub('contact', {...c, name: e.target.value})} /></td>
                          <td className="p-0 border-r border-slate-100"><input type="text" className="w-full p-6 outline-none text-center" value={c.position} onChange={e => updateSub('contact', {...c, position: e.target.value})} /></td>
                          <td className="p-0 border-r border-slate-100"><input type="text" className="w-full p-6 outline-none text-center text-blue-600 font-mono" value={c.mobile} onChange={e => updateSub('contact', {...c, mobile: e.target.value})} /></td>
                          <td className="p-0"><input type="text" className="w-full p-6 outline-none" value={c.note || ''} onChange={e => updateSub('contact', {...c, note: e.target.value})} /></td>
                          <td className="p-6 text-center"><button onClick={async () => await deleteDoc(doc(db, 'artifacts', appId, 'public', 'data', `contacts_${activeSiteId}`, c.id))} className="text-slate-200 hover:text-red-500 transition-colors"><Trash2 size={28}/></button></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
              {/* 상담 일지 */}
              <section>
                <div className="flex justify-between items-end mb-12 px-6">
                  <h2 className="text-4xl font-black text-slate-900 flex items-center gap-5"><div className="w-5 h-14 bg-cyan-600 rounded-full" /> 상세 상담 및 업무 기록</h2>
                  <button onClick={() => updateSub('log', { date: new Date().toISOString().split('T')[0], type: '', content: '' })} className="px-10 py-5 bg-cyan-700 text-white rounded-[32px] font-black flex items-center gap-4 shadow-2xl transition-all hover:scale-105 active:scale-95"><Plus size={28} /> 일지 작성</button>
                </div>
                <div className="overflow-x-auto border border-slate-200 rounded-[56px] shadow-2xl bg-white">
                  <table className="w-full border-collapse min-w-[1200px] font-bold text-lg">
                    <thead className="bg-cyan-700 text-white uppercase text-sm">
                      <tr><th className="p-6 border-r border-cyan-600/50 w-56 text-center">상담일</th><th className="p-6 border-r border-cyan-600/50 w-64">업무형태</th><th className="p-6 border-r border-cyan-600/50">내용</th><th className="p-6 w-20 bg-white"></th></tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {consultationLogs.map(l => (
                        <tr key={l.id} className="hover:bg-cyan-50/30 transition-colors">
                          <td className="p-0 border-r border-slate-100"><input type="date" className="w-full p-6 outline-none font-bold text-center text-xl" value={l.date} onChange={e => updateSub('log', {...l, date: e.target.value})} /></td>
                          <td className="p-0 border-r border-slate-100"><input type="text" className="w-full p-6 outline-none font-bold text-center" placeholder="..." value={l.type} onChange={e => updateSub('log', {...l, type: e.target.value})} /></td>
                          <td className="p-0 border-r border-slate-100"><textarea rows="1" className="w-full p-6 outline-none font-bold resize-none overflow-hidden leading-relaxed" value={l.content} onChange={e => updateSub('log', {...l, content: e.target.value})} onInput={e => {e.target.style.height = 'auto'; e.target.style.height = e.target.scrollHeight + 'px';}} /></td>
                          <td className="p-6 text-center"><button onClick={async () => await deleteDoc(doc(db, 'artifacts', appId, 'public', 'data', `logs_${activeSiteId}`, l.id))} className="text-slate-200 hover:text-red-500 transition-colors"><Trash2 size={28}/></button></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </>
          ) : (
            <div className="p-40 bg-slate-50 rounded-[70px] border-4 border-dashed border-slate-200 text-center text-slate-300 font-black text-4xl">먼저 기본 정보를 저장하여 관리 번호를 등록해 주세요.</div>
          )}
          <div className="flex justify-center pt-20"><button onClick={() => onSave(formData)} className="px-60 py-12 bg-slate-950 text-white rounded-[40px] hover:bg-black hover:scale-105 transition-all shadow-[0_50px_100px_rgba(0,0,0,0.5)] font-black text-5xl active:scale-95">최종 데이터 저장</button></div>
        </div>
      </div>
    </div>
  );
};
// --- [공통 UI 박스] ---
const InputBox = ({ label, value, onChange, fullWidth = false, highlight = false, multiline = false }) => {
  const ref = useRef(null);
  useEffect(() => { if (multiline && ref.current) { ref.current.style.height = 'auto'; ref.current.style.height = ref.current.scrollHeight + 'px'; } }, [value, multiline]);
  return (
    <div className={`flex flex-col border-b border-r border-slate-100 py-10 px-14 group hover:bg-slate-50 transition-colors ${fullWidth ? 'md:col-span-2 lg:col-span-3 border-r-0' : ''}`}>
      <label className="text-[16px] font-black text-slate-400 uppercase mb-4 group-focus-within:text-blue-600 tracking-[0.2em] leading-none">{label}</label>
      {multiline ? <textarea ref={ref} className="bg-transparent outline-none border-none p-0 text-3xl font-black resize-none overflow-hidden text-slate-800 leading-tight" value={value} onChange={(e) => onChange(e.target.value)} rows={1} /> : <input type="text" className={`bg-transparent outline-none border-none p-0 text-3xl font-black ${highlight ? 'text-blue-800' : 'text-slate-900'}`} value={value} onChange={(e) => onChange(e.target.value)} />}
    </div>
  );
};
const DisplayBox = ({ label, value, color = "text-slate-700", bg = "bg-white" }) => (
  <div className={`flex flex-col border-b border-r border-slate-100 py-10 px-14 ${bg}`}>
    <span className="text-[16px] font-black text-slate-300 uppercase mb-4 tracking-[0.2em] leading-none">{label}</span>
    <span className={`text-3xl font-black ${color}`}>{value}</span>
  </div>
);
const StatusBadge = ({ label, value, color }) => (
  <div className={`bg-white/10 backdrop-blur-md p-8 rounded-[40px] border border-white/20 text-center min-w-[200px] shadow-2xl`}>
    <p className={`text-[12px] font-black uppercase tracking-[0.3em] mb-2 ${color === 'red' ? 'text-red-400' : 'text-slate-400'}`}>{label}</p>
    <p className={`text-4xl font-black ${color === 'blue' ? 'text-blue-400' : color === 'orange' ? 'text-orange-400' : 'text-red-500'}`}>{value}</p>
  </div>
);
const LinkEditModal = ({ link, onSave, onDelete, onClose }) => {
  const [title, setTitle] = useState(link?.title || '');
  const [url, setUrl] = useState(link?.url || '');
  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/90 backdrop-blur-3xl animate-in fade-in duration-500">
      <div className="bg-white w-full max-w-2xl rounded-[80px] shadow-[0_50px_100px_rgba(0,0,0,0.8)] overflow-hidden">
        <div className="p-14 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h3 className="text-4xl font-black text-slate-900 tracking-tighter leading-none">QUICK LINK</h3>
          <button onClick={onClose} className="p-4 text-slate-300 hover:text-slate-900 transition-colors"><X size={48}/></button>
        </div>
        <div className="p-14 space-y-12">
          <div className="space-y-4">
            <label className="text-[14px] font-black text-slate-400 uppercase tracking-widest ml-3">아이콘 제목</label>
            <input type="text" className="w-full px-10 py-8 bg-slate-100 border-none rounded-[40px] focus:ring-8 focus:ring-blue-100 outline-none font-black text-slate-800 text-3xl" value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="space-y-4">
            <label className="text-[14px] font-black text-slate-400 uppercase tracking-widest ml-3">URL (https://...)</label>
            <input type="text" className="w-full px-10 py-8 bg-slate-100 border-none rounded-[40px] focus:ring-8 focus:ring-blue-100 outline-none font-bold text-slate-600 font-mono text-xl" value={url} onChange={(e) => setUrl(e.target.value)} />
          </div>
        </div>
        <div className="p-14 pt-0 flex justify-between">
          {link ? <button onClick={() => onDelete(link.id)} className="text-red-500 font-black hover:bg-red-50 px-10 py-5 rounded-[30px] text-xl">DELETE</button> : <div />}
          <div className="flex gap-6">
            <button onClick={onClose} className="px-10 py-5 text-slate-400 font-black text-xl hover:text-slate-900">CLOSE</button>
            <button onClick={() => onSave(title, url)} className="px-20 py-6 bg-blue-600 text-white font-black rounded-[40px] hover:bg-blue-700 shadow-2xl text-2xl">SAVE</button>
          </div>
        </div>
      </div>
    </div>
  );
};
export default App;


