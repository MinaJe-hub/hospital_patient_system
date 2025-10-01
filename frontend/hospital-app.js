// API 설정
const API_BASE_URL = 'http://localhost:8000';

// 전역 상태
let currentPatient = null;
let searchResults = [];

// DOM 로드 완료 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

// 앱 초기화
function initializeApp() {
    // 현재 날짜 표시
    updateDateTime();
    setInterval(updateDateTime, 60000);
    
    // 통계 로드
    loadDashboardStats();
    setInterval(loadDashboardStats, 30000);
    
    // 최근 활동 로드
    loadRecentVisits();
    
    // 네비게이션 이벤트 설정
    setupNavigation();
    
    // 검색 이벤트 설정
    setupSearch();
    
    // 탭 이벤트 설정
    setupTabs();
}

// 날짜/시간 업데이트
function updateDateTime() {
    const now = new Date();
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    const dateStr = now.toLocaleDateString('ko-KR', options);
    document.getElementById('currentDate').textContent = dateStr;
}

// 대시보드 통계 로드
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/patients/stats/today`);
        if (!response.ok) throw new Error('통계 로드 실패');
        
        const stats = await response.json();
        
        // 애니메이션과 함께 숫자 업데이트
        animateNumber('totalPatients', stats.total_patients || 0);
        animateNumber('todayVisits', stats.today_visits || 0);
        animateNumber('todayAppointments', stats.today_appointments || 0);
        animateNumber('waitingPatients', stats.waiting_patients || 0);
    } catch (error) {
        console.error('통계 로드 오류:', error);
    }
}

// 숫자 애니메이션
function animateNumber(elementId, targetNumber) {
    const element = document.getElementById(elementId);
    const currentNumber = parseInt(element.textContent) || 0;
    const increment = (targetNumber - currentNumber) / 20;
    let current = currentNumber;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= targetNumber) || (increment < 0 && current <= targetNumber)) {
            element.textContent = targetNumber;
            clearInterval(timer);
        } else {
            element.textContent = Math.round(current);
        }
    }, 50);
}

// 최근 진료 활동 로드
async function loadRecentVisits() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/visits/today`);
        if (!response.ok) throw new Error('진료 기록 로드 실패');
        
        const visits = await response.json();
        const activityList = document.getElementById('recentActivity');
        
        if (visits.length === 0) {
            activityList.innerHTML = '<div class="empty-state"><h3>오늘 진료 기록이 없습니다</h3></div>';
            return;
        }
        
        activityList.innerHTML = visits.slice(0, 5).map(visit => `
            <div class="activity-item">
                <div class="activity-time">${formatTime(visit.visit_date)}</div>
                <div class="activity-content">
                    <p class="activity-patient">${visit.patient_name} (${visit.patient_no})</p>
                    <p class="activity-details">${visit.department} | ${visit.doctor_name} | ${visit.diagnosis}</p>
                </div>
                <span class="activity-status ${getStatusClass(visit.status)}">${visit.status}</span>
            </div>
        `).join('');
    } catch (error) {
        console.error('최근 활동 로드 오류:', error);
        document.getElementById('recentActivity').innerHTML = '<div class="empty-state"><h3>데이터를 불러올 수 없습니다</h3></div>';
    }
}

// 네비게이션 설정
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const pages = document.querySelectorAll('.page');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            // 활성 네비게이션 변경
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // 페이지 변경
            const targetPage = item.dataset.page;
            pages.forEach(page => page.classList.remove('active'));
            const targetPageElement = document.getElementById(`${targetPage}Page`);
            if (targetPageElement) {
                targetPageElement.classList.add('active');
            }
            
            // 페이지 제목 변경
            const pageTitle = document.getElementById('pageTitle');
            pageTitle.textContent = item.querySelector('span:last-child').textContent;
        });
    });
}

// 검색 설정
function setupSearch() {
    // 빠른 검색
    const quickSearchBtn = document.getElementById('quickSearchBtn');
    const quickSearchInput = document.getElementById('quickSearchInput');
    
    quickSearchBtn.addEventListener('click', () => {
        const query = quickSearchInput.value.trim();
        if (query) performSearch(query);
    });
    
    quickSearchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = e.target.value.trim();
            if (query) performSearch(query);
        }
    });
    
    // 환자 검색 페이지
    const patientSearchInput = document.getElementById('patientSearchInput');
    if (patientSearchInput) {
        patientSearchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchPatients();
            }
        });
    }
}

// 환자 검색 실행
async function searchPatients() {
    const input = document.getElementById('patientSearchInput');
    const query = input.value.trim();
    
    if (!query) {
        showToast('검색어를 입력해주세요', 'warning');
        return;
    }
    
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '<div class="loading">검색 중...</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/patients/search?query=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('검색 실패');
        
        const patients = await response.json();
        searchResults = patients;
        
        if (patients.length === 0) {
            resultsDiv.innerHTML = '<div class="empty-state"><h3>검색 결과가 없습니다</h3><p>다른 검색어로 시도해보세요</p></div>';
            return;
        }
        
        // 검색 결과 테이블 생성
        resultsDiv.innerHTML = `
            <table class="results-table">
                <thead>
                    <tr>
                        <th>환자번호</th>
                        <th>이름</th>
                        <th>생년월일</th>
                        <th>성별</th>
                        <th>연락처</th>
                        <th>진료횟수</th>
                        <th>마지막 방문</th>
                        <th>작업</th>
                    </tr>
                </thead>
                <tbody>
                    ${patients.map(patient => `
                        <tr>
                            <td>
                                <span class="patient-id">${patient.patient_no}</span>
                            </td>
                            <td>
                                <span class="patient-name">${patient.name}</span>
                            </td>
                            <td>${formatDate(patient.birth_date)}</td>
                            <td>${patient.gender === 'M' ? '남' : '여'}</td>
                            <td>${patient.phone}</td>
                            <td>${patient.visit_count || 0}회</td>
                            <td>${patient.last_visit_date ? formatDate(patient.last_visit_date) : '-'}</td>
                            <td>
                                <button class="btn-view" onclick="showPatientDetail(${patient.patient_id})">
                                    상세보기
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        showToast(`${patients.length}명의 환자를 찾았습니다`, 'success');
    } catch (error) {
        console.error('검색 오류:', error);
        resultsDiv.innerHTML = '<div class="empty-state"><h3>검색 중 오류가 발생했습니다</h3></div>';
        showToast('검색 실패', 'error');
    }
}

// 빠른 검색 실행
async function performSearch(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/patients/search?query=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('검색 실패');
        
        const patients = await response.json();
        
        if (patients.length === 0) {
            showToast('검색 결과가 없습니다', 'info');
            return;
        }
        
        if (patients.length === 1) {
            // 한 명만 찾았으면 바로 상세 보기
            showPatientDetail(patients[0].patient_id);
        } else {
            // 여러 명이면 환자 검색 페이지로 이동
            document.querySelector('[data-page="patients"]').click();
            document.getElementById('patientSearchInput').value = query;
            searchPatients();
        }
    } catch (error) {
        console.error('빠른 검색 오류:', error);
        showToast('검색 실패', 'error');
    }
}

// 환자 상세 정보 표시
async function showPatientDetail(patientId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/patients/${patientId}`);
        if (!response.ok) throw new Error('환자 정보 로드 실패');
        
        const data = await response.json();
        currentPatient = data.patient;
        
        // 모달 제목
        document.getElementById('modalTitle').textContent = `${data.patient.name} 님의 정보`;
        
        // 기본 정보
        const age = calculateAge(data.patient.birth_date);
        document.getElementById('patientDetailHeader').innerHTML = `
            <div class="patient-info-grid">
                <div class="info-group">
                    <label>환자번호</label>
                    <p>${data.patient.patient_no}</p>
                </div>
                <div class="info-group">
                    <label>이름</label>
                    <p>${data.patient.name}</p>
                </div>
                <div class="info-group">
                    <label>생년월일</label>
                    <p>${formatDate(data.patient.birth_date)} (${age}세)</p>
                </div>
                <div class="info-group">
                    <label>성별</label>
                    <p>${data.patient.gender === 'M' ? '남성' : '여성'}</p>
                </div>
                <div class="info-group">
                    <label>연락처</label>
                    <p>${data.patient.phone}</p>
                </div>
                <div class="info-group">
                    <label>등록일</label>
                    <p>${formatDate(data.patient.created_at)}</p>
                </div>
            </div>
        `;
        
        // 진료 이력
        const visitsPanel = document.getElementById('visitsPanel');
        if (data.visits && data.visits.length > 0) {
            visitsPanel.innerHTML = data.visits.map(visit => `
                <div class="visit-card">
                    <div class="visit-header">
                        <span class="visit-date">${formatDateTime(visit.visit_date)}</span>
                        <span class="visit-status status-completed">${visit.status}</span>
                    </div>
                    <div class="visit-content">
                        <p><strong>${visit.department}</strong> | ${visit.doctor_name}</p>
                        <p>진단: ${visit.diagnosis}</p>
                    </div>
                </div>
            `).join('');
        } else {
            visitsPanel.innerHTML = '<div class="empty-state"><h3>진료 이력이 없습니다</h3></div>';
        }
        
        // 예약 현황
        const appointmentsPanel = document.getElementById('appointmentsPanel');
        if (data.appointments && data.appointments.length > 0) {
            appointmentsPanel.innerHTML = data.appointments.map(apt => `
                <div class="visit-card">
                    <div class="visit-header">
                        <span class="visit-date">${formatDateTime(apt.appointment_date)}</span>
                        <span class="visit-status ${getAppointmentStatusClass(apt.status)}">${apt.status}</span>
                    </div>
                    <div class="visit-content">
                        <p><strong>${apt.department}</strong> | ${apt.doctor_name}</p>
                    </div>
                </div>
            `).join('');
        } else {
            appointmentsPanel.innerHTML = '<div class="empty-state"><h3>예약이 없습니다</h3></div>';
        }
        
        // 모달 열기
        openModal();
    } catch (error) {
        console.error('환자 정보 로드 오류:', error);
        showToast('환자 정보를 불러올 수 없습니다', 'error');
    }
}

// 탭 설정
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.dataset.tab;
            
            // 버튼 활성화
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // 패널 전환
            tabPanels.forEach(panel => panel.classList.remove('active'));
            document.getElementById(`${targetTab}Panel`).classList.add('active');
        });
    });
}

// 모달 열기
function openModal() {
    const modal = document.getElementById('patientModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// 모달 닫기
function closeModal() {
    const modal = document.getElementById('patientModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
    currentPatient = null;
}

// ========== 신규 환자 등록 기능 ==========
function showNewPatientForm() {
    // 폼 초기화
    document.getElementById('newPatientForm').reset();
    
    // 환자번호 자동 생성
    const currentYear = new Date().getFullYear();
    const randomNum = Math.floor(Math.random() * 9000) + 1000;
    document.getElementById('patientNo').value = `P${currentYear}${randomNum}`;
    
    // 모달 열기
    const modal = document.getElementById('newPatientModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeNewPatientModal() {
    const modal = document.getElementById('newPatientModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

async function saveNewPatient() {
    const form = document.getElementById('newPatientForm');
    
    // 폼 유효성 검사
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // 폼 데이터 수집
    const formData = new FormData(form);
    const patientData = {};
    for (let [key, value] of formData.entries()) {
        patientData[key] = value;
    }
    
    // 전화번호 형식 정리 (하이픈 제거)
    patientData.phone = patientData.phone.replace(/-/g, '');
    
    // 로딩 표시
    const submitBtn = document.querySelector('#newPatientModal .btn-primary');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '등록 중...';
    submitBtn.disabled = true;
    
    try {
        // API 호출
        const response = await fetch(`${API_BASE_URL}/api/patients`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(patientData)
        });
        
        if (!response.ok) {
            if (response.status === 400) {
                const error = await response.json();
                throw new Error(error.detail || '환자 등록에 실패했습니다.');
            }
            throw new Error('환자 등록에 실패했습니다.');
        }
        
        const result = await response.json();
        
        // 성공 메시지
        showToast('환자가 성공적으로 등록되었습니다!', 'success');
        
        // 모달 닫기
        closeNewPatientModal();
        
        // 환자 목록 새로고침 (검색 페이지에 있다면)
        const currentPage = document.querySelector('.nav-item.active').dataset.page;
        if (currentPage === 'patients') {
            document.getElementById('patientSearchInput').value = patientData.patient_no;
            searchPatients();
        }
        
    } catch (error) {
        console.error('환자 등록 오류:', error);
        showToast(error.message || '환자 등록 중 오류가 발생했습니다.', 'error');
    } finally {
        // 버튼 복원
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// ========== 진료 등록 기능 ==========
function showNewVisitForm() {
    if (!currentPatient) {
        showToast('환자를 먼저 선택해주세요', 'warning');
        return;
    }
    
    // 진료 등록 모달에 환자 정보 표시
    document.getElementById('visitPatientName').textContent = currentPatient.name;
    document.getElementById('visitPatientNo').textContent = currentPatient.patient_no;
    
    // 폼 초기화
    document.getElementById('newVisitForm').reset();
    document.getElementById('visitDate').value = new Date().toISOString().slice(0, 16);
    
    // 모달 열기
    closeModal(); // 환자 상세 모달 닫기
    const modal = document.getElementById('newVisitModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeNewVisitModal() {
    const modal = document.getElementById('newVisitModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

async function saveNewVisit() {
    const form = document.getElementById('newVisitForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const formData = new FormData(form);
    const visitData = {
        patient_id: currentPatient.patient_id,
        visit_date: formData.get('visit_date'),
        department: formData.get('department'),
        doctor_name: formData.get('doctor_name'),
        diagnosis: formData.get('diagnosis'),
        status: formData.get('status')
    };
    
    const submitBtn = document.querySelector('#newVisitModal .btn-primary');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '등록 중...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/visits`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(visitData)
        });
        
        if (!response.ok) throw new Error('진료 등록 실패');
        
        showToast('진료 기록이 등록되었습니다', 'success');
        closeNewVisitModal();
        
        // 환자 상세 정보 새로고침
        showPatientDetail(currentPatient.patient_id);
        
    } catch (error) {
        console.error('진료 등록 오류:', error);
        showToast('진료 등록 중 오류가 발생했습니다', 'error');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// ========== 예약 추가 기능 ==========
function showNewAppointmentForm() {
    if (!currentPatient) {
        showToast('환자를 먼저 선택해주세요', 'warning');
        return;
    }
    
    // 예약 모달에 환자 정보 표시
    document.getElementById('appointmentPatientName').textContent = currentPatient.name;
    document.getElementById('appointmentPatientNo').textContent = currentPatient.patient_no;
    
    // 폼 초기화
    document.getElementById('newAppointmentForm').reset();
    
    // 모달 열기
    closeModal(); // 환자 상세 모달 닫기
    const modal = document.getElementById('newAppointmentModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeNewAppointmentModal() {
    const modal = document.getElementById('newAppointmentModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

async function saveNewAppointment() {
    const form = document.getElementById('newAppointmentForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const formData = new FormData(form);
    const appointmentData = {
        patient_id: currentPatient.patient_id,
        appointment_date: formData.get('appointment_date'),
        department: formData.get('department'),
        doctor_name: formData.get('doctor_name'),
        status: '예약'
    };
    
    const submitBtn = document.querySelector('#newAppointmentModal .btn-primary');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '등록 중...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/appointments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(appointmentData)
        });
        
        if (!response.ok) throw new Error('예약 등록 실패');
        
        showToast('예약이 등록되었습니다', 'success');
        closeNewAppointmentModal();
        
        // 환자 상세 정보 새로고침
        showPatientDetail(currentPatient.patient_id);
        
    } catch (error) {
        console.error('예약 등록 오류:', error);
        showToast('예약 등록 중 오류가 발생했습니다', 'error');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// 전화번호 입력 시 자동 포맷팅
function formatPhoneInput(input) {
    let value = input.value.replace(/[^\d]/g, '');
    
    if (value.length <= 3) {
        input.value = value;
    } else if (value.length <= 7) {
        input.value = value.slice(0, 3) + '-' + value.slice(3);
    } else if (value.length <= 11) {
        input.value = value.slice(0, 3) + '-' + value.slice(3, 7) + '-' + value.slice(7);
    }
}

// 토스트 메시지 표시
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 유틸리티 함수
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function calculateAge(birthDate) {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
    }
    
    return age;
}

function getStatusClass(status) {
    switch(status) {
        case '완료': return 'completed';
        case '대기': return 'waiting';
        case '진료중': return 'in-progress';
        default: return '';
    }
}

function getAppointmentStatusClass(status) {
    switch(status) {
        case '예약': return 'status-scheduled';
        case '취소': return 'status-cancelled';
        case '완료': return 'status-completed';
        default: return '';
    }
}

// ESC 키로 모달 닫기
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
        closeNewPatientModal();
        closeNewVisitModal();
        closeNewAppointmentModal();
    }
});