-- Supabase 테이블 생성 스크립트
-- log, report, history 테이블 생성

-- 1. log 테이블 생성
CREATE TABLE IF NOT EXISTS log (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP,
    device_ip VARCHAR(15),
    device_name VARCHAR(255),
    source_institution_code VARCHAR(50),
    source_ip VARCHAR(15),
    source_port INTEGER,
    source_asset_name VARCHAR(255),
    source_country VARCHAR(100),
    source_mac VARCHAR(17),
    dest_institution_code VARCHAR(50),
    dest_ip VARCHAR(15),
    dest_port INTEGER,
    dest_asset_name VARCHAR(255),
    dest_country VARCHAR(100),
    dest_mac VARCHAR(17),
    protocol VARCHAR(50),
    action VARCHAR(100),
    attack_type VARCHAR(100),
    account VARCHAR(255),
    risk_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. history 테이블 생성 (log 테이블의 모든 컬럼 + 추가 컬럼들)
CREATE TABLE IF NOT EXISTS history (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP,
    device_ip VARCHAR(15),
    device_name VARCHAR(255),
    source_institution_code VARCHAR(50),
    source_ip VARCHAR(15),
    source_port INTEGER,
    source_asset_name VARCHAR(255),
    source_country VARCHAR(100),
    source_mac VARCHAR(17),
    dest_institution_code VARCHAR(50),
    dest_ip VARCHAR(15),
    dest_port INTEGER,
    dest_asset_name VARCHAR(255),
    dest_country VARCHAR(100),
    dest_mac VARCHAR(17),
    protocol VARCHAR(50),
    action VARCHAR(100),
    attack_type VARCHAR(100),
    account VARCHAR(255),
    risk_level VARCHAR(50),
    given_script TEXT,
    executed_script TEXT,
    changed_reason TEXT,
    caution_level INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. report 테이블 생성
CREATE TABLE IF NOT EXISTS report (
    id SERIAL PRIMARY KEY,
    report TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성 (성능 향상을 위해)
CREATE INDEX IF NOT EXISTS idx_log_event_time ON log(event_time);
CREATE INDEX IF NOT EXISTS idx_log_source_ip ON log(source_ip);
CREATE INDEX IF NOT EXISTS idx_log_dest_ip ON log(dest_ip);
CREATE INDEX IF NOT EXISTS idx_log_attack_type ON log(attack_type);

CREATE INDEX IF NOT EXISTS idx_history_event_time ON history(event_time);
CREATE INDEX IF NOT EXISTS idx_history_source_ip ON history(source_ip);
CREATE INDEX IF NOT EXISTS idx_history_dest_ip ON history(dest_ip);
CREATE INDEX IF NOT EXISTS idx_history_caution_level ON history(caution_level);

CREATE INDEX IF NOT EXISTS idx_report_created_at ON report(created_at);

-- 코멘트 추가
COMMENT ON TABLE log IS '보안 로그 테이블 - 원본 로그 데이터 저장';
COMMENT ON TABLE history IS '히스토리 테이블 - 처리된 로그와 스크립트 실행 기록 저장';
COMMENT ON TABLE report IS '리포트 테이블 - 생성된 보고서 저장';

COMMENT ON COLUMN log.id IS '로그 고유 ID (자동 증가)';
COMMENT ON COLUMN log.event_time IS '이벤트 발생 시간';
COMMENT ON COLUMN log.risk_level IS '위험도 수준';

COMMENT ON COLUMN history.given_script IS 'AI가 제안한 스크립트';
COMMENT ON COLUMN history.executed_script IS '실제 실행된 스크립트';
COMMENT ON COLUMN history.changed_reason IS '스크립트 변경 이유';
COMMENT ON COLUMN history.caution_level IS '주의 수준 (0: 일반, 1: 주의)';

COMMENT ON COLUMN report.report IS '생성된 보고서 내용';
