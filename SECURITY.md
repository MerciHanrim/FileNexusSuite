# Security Policy · 보안 정책

## 지원 버전 · Supported Versions

현재 보안 업데이트는 다음 버전에 제공됩니다:

Security updates are provided for the following versions:

| Version | Supported |
| ------- | :-------: |
| 1.1.3   | Yes |
| < 1.1.3 | No |

## 취약점 제보 · Reporting a Vulnerability

File Nexus Suite에서 보안 취약점을 발견하셨다면, **공개 Issue로 보고하지 마시고** 아래 방법으로 제보 부탁드립니다.

If you find a security vulnerability in File Nexus Suite, **please do not report it through public Issues**. Instead, please use the methods below.

### 제보 방법 · How to Report

- **이메일 · Email**: [pieceofspring@gmail.com](mailto:pieceofspring@gmail.com)
- **GitHub Security Advisory**: [Report a vulnerability](https://github.com/MerciHanrim/FileNexusSuite/security/advisories/new)

### 제보 시 포함해주시면 좋은 정보 · Helpful Information

- 취약점 유형 · Type of vulnerability
- 영향 받는 버전 · Affected version(s)
- 재현 절차 · Reproduction steps
- 예상되는 영향 · Potential impact
- (가능한 경우) 수정 제안 · Suggested fix (if applicable)

### 대응 소요 시간 · Response Time

본 프로젝트는 **개인이 AI 페어 프로그래밍으로 개발하는 오픈소스 프로젝트입니다.** 전담 보안팀은 없으나, 제보된 사항은 최대한 빠르게 확인하고 대응하도록 노력하겠습니다.

This is an **open-source project** developed individually with AI pair programming. There is no dedicated security team, but I will do my best to review and respond to reports as quickly as possible.

- 최초 응답 · Initial response: 1~7일 이내 · Within 1-7 days
- 수정 시점 · Patch availability: 사안의 심각도에 따라 결정 · Depends on severity

## 파일 처리 관련 주의사항 · File Handling Notes

File Nexus Suite는 로컬 파일을 읽고 쓰는 도구입니다. 다음 사항을 유의해 주세요.

File Nexus Suite reads and writes local files. Please note the following.

- 중요한 파일은 **작업 전 반드시 백업**하세요.  
  Always **back up important files** before processing.
- 본 도구는 **네트워크 전송·클라우드 업로드 기능을 포함하지 않습니다**.  
  This tool does **not include network transmission or cloud upload features**.
- 모든 처리는 **사용자의 로컬 환경에서만** 이루어집니다.  
  All processing is performed **only on the user's local machine**.

---

Copyright © 2026 Hanrim
