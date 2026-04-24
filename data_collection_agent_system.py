#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于Agent编程的软件系统 - 云南省企业就业失业数据采集系统智能助手
这是一个演示用的人工智能Agent系统，展示如何使用Agent技术辅助项目管理和数据处理
"""

import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class User:
    id: str
    name: str
    role: str  # 'enterprise', 'city', 'province'
    company_id: str = None
    region: str = None

@dataclass
class Report:
    id: str
    company_id: str
    period: str
    employment_data: Dict
    status: str  # 'draft', 'submitted', 'reviewed', 'rejected', 'approved'
    submit_time: datetime
    review_time: datetime = None
    review_result: str = None

class DataCollectionAgent:
    """数据采集Agent - 负责数据收集和验证"""

    def __init__(self):
        self.report_rules = {
            'max_employment': 10000,
            'min_employment': 0,
            'required_fields': ['company_id', 'employment_count', 'change_reason']
        }

    def validate_report(self, data: Dict) -> Dict:
        """验证数据完整性"""
        errors = []

        # 检查必填字段
        for field in self.report_rules['required_fields']:
            if field not in data or not data[field]:
                errors.append(f"缺少必填字段: {field}")

        # 检查就业人数范围
        if 'employment_count' in data:
            try:
                count = int(data['employment_count'])
                if count < 0 or count > self.report_rules['max_employment']:
                    errors.append("就业人数范围不正确")
            except ValueError:
                errors.append("就业人数必须是数字")

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'suggestions': self._generate_suggestions(data)
        }

    def _generate_suggestions(self, data: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []

        if data.get('change_reason') and '订单' in str(data['change_reason']):
            suggestions.append("建议关注订单变化对就业的影响")
        if data.get('employment_count') and int(data['employment_count']) < 50:
            suggestions.append("小微企业的就业数据需要特别关注")

        return suggestions

class ReviewAgent:
    """审核Agent - 负责数据审核和异常检测"""

    def __init__(self):
        self.anomaly_threshold = {
            'employment_change_rate': 0.2,  # 20%
            'data_suspicion_score': 0.7
        }

    def review_report(self, report: Report, historical_data: List[Dict]) -> Dict:
        """审核报告"""
        review_result = {
            'report_id': report.id,
            'anomalies': [],
            'risk_level': 'low',
            'recommendation': 'approve'
        }

        # 检查数据异常
        anomalies = self._check_anomalies(report, historical_data)
        review_result['anomalies'] = anomalies

        # 评估风险等级
        if len(anomalies) > 2:
            review_result['risk_level'] = 'high'
            review_result['recommendation'] = 'reject'
        elif len(anomalies) > 0:
            review_result['risk_level'] = 'medium'
            review_result['recommendation'] = 'review'

        return review_result

    def _check_anomalies(self, report: Report, historical_data: List[Dict]) -> List[str]:
        """检查异常情况"""
        anomalies = []

        # 查找历史数据
        previous_data = next((data for data in historical_data
                            if data['period'] == self._get_previous_period(report.period)), None)

        if previous_data:
            # 检查就业人数变化率
            current = report.employment_data.get('employment_count', 0)
            previous = previous_data.get('employment_count', 0)

            if previous > 0:
                change_rate = abs(current - previous) / previous
                if change_rate > self.anomaly_threshold['employment_change_rate']:
                    anomalies.append(f"就业人数变化率过高: {change_rate:.2%}")

        return anomalies

class AnalysisAgent:
    """分析Agent - 负责数据分析和趋势预测"""

    def __init__(self):
        self.trend_window = 6  # 6个月趋势分析

    def analyze_trend(self, reports: List[Report]) -> Dict:
        """分析就业趋势"""
        period_data = {}

        # 按周期聚合数据
        for report in reports:
            if report.status == 'approved':
                period_data.setdefault(report.period, {
                    'total_employment': 0,
                    'company_count': 0,
                    'companies': []
                })
                period_data[report.period]['total_employment'] += report.employment_data.get('employment_count', 0)
                period_data[report.period]['company_count'] += 1
                period_data[report.period]['companies'].append(report.company_id)

        # 计算趋势
        periods = sorted(period_data.keys())
        trend_analysis = {
            'periods': periods,
            'employment_trend': self._calculate_trend(period_data, periods, 'total_employment'),
            'growth_rate': self._calculate_growth_rate(periods, period_data),
            'regional_distribution': self._analyze_distribution(reports)
        }

        return trend_analysis

    def _calculate_trend(self, period_data: Dict, periods: List, metric: str) -> str:
        """计算趋势"""
        if len(periods) < 3:
            return 'data_insufficient'

        values = [period_data[p][metric] for p in periods[-3:]]

        if values[2] > values[1] and values[1] > values[0]:
            return 'increasing'
        elif values[2] < values[1] and values[1] < values[0]:
            return 'decreasing'
        else:
            return 'stable'

    def _calculate_growth_rate(self, periods: List, period_data: Dict) -> float:
        """计算增长率"""
        if len(periods) < 2:
            return 0.0

        current = period_data[periods[-1]]['total_employment']
        previous = period_data[periods[-2]]['total_employment']

        if previous == 0:
            return 0.0

        return (current - previous) / previous * 100

    def _analyze_distribution(self, reports: List[Report]) -> Dict:
        """分析区域分布"""
        regional_data = {}

        for report in reports:
            if report.status == 'approved':
                # 简化的区域获取方法
                region = f"地区{hash(report.company_id) % 10}"  # 模拟10个地区
                regional_data.setdefault(region, {
                    'employment': 0,
                    'companies': 0
                })
                regional_data[region]['employment'] += report.employment_data.get('employment_count', 0)
                regional_data[region]['companies'] += 1

        return regional_data

class SmartNotificationAgent:
    """智能通知Agent - 负责发送个性化通知"""

    def __init__(self):
        self.notification_templates = {
            'reminder': {
                'enterprise': '尊敬的企业负责人，您的月度就业失业数据填报即将到期，请及时提交。',
                'city': '市局管理员，辖区内有{count}家企业尚未提交数据，请及时催报。'
            },
            'approval': {
                'enterprise': '您的数据审核通过，感谢配合！',
                'city': '辖区内数据审核完成，共通过{count}家企业数据。'
            },
            'alert': {
                'enterprise': '您的数据已被退回，原因：{reason}，请修改后重新提交。',
                'city': '发现异常数据，已标记需要重点审核。'
            }
        }

    def generate_notification(self, type: str, role: str, **kwargs) -> str:
        """生成通知内容"""
        template = self.notification_templates[type][role]
        return template.format(**kwargs)

class DataCollectionSystem:
    """数据采集系统主控类"""

    def __init__(self):
        self.data_collection_agent = DataCollectionAgent()
        self.review_agent = ReviewAgent()
        self.analysis_agent = AnalysisAgent()
        self.notification_agent = SmartNotificationAgent()

        self.users = {}
        self.reports = {}
        self.historical_data = []

    def add_user(self, user: User):
        """添加用户"""
        self.users[user.id] = user

    def submit_report(self, user_id: str, data: Dict) -> Dict:
        """提交报告"""
        if user_id not in self.users:
            return {'success': False, 'message': '用户不存在'}

        user = self.users[user_id]
        if user.role != 'enterprise':
            return {'success': False, 'message': '只有企业可以提交数据'}

        # 验证数据
        validation_result = self.data_collection_agent.validate_report(data)

        if not validation_result['is_valid']:
            return {
                'success': False,
                'message': '数据验证失败',
                'errors': validation_result['errors'],
                'suggestions': validation_result['suggestions']
            }

        # 创建报告
        report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        report = Report(
            id=report_id,
            company_id=user.company_id,
            period=datetime.now().strftime('%Y%m'),
            employment_data=data,
            status='submitted',
            submit_time=datetime.now()
        )

        self.reports[report_id] = report

        # 通知企业提交成功
        notification = self.notification_agent.generate_notification(
            'approval', 'enterprise'
        )

        return {
            'success': True,
            'report_id': report_id,
            'message': '数据提交成功',
            'notification': notification
        }

    def review_report(self, reviewer_id: str, report_id: str, action: str, reason: str = None) -> Dict:
        """审核报告"""
        if report_id not in self.reports:
            return {'success': False, 'message': '报告不存在'}

        report = self.reports[report_id]
        if report.status != 'submitted':
            return {'success': False, 'message': '该报告已被审核'}

        # 执行审核
        review_result = self.review_agent.review_report(report, self.historical_data)

        if action == 'approve':
            report.status = 'approved'
            report.review_time = datetime.now()
            report.review_result = '审核通过'

            # 添加到历史数据
            self.historical_data.append({
                'report_id': report.id,
                'company_id': report.company_id,
                'period': report.period,
                'employment_count': report.employment_data.get('employment_count', 0),
                'review_time': report.review_time
            })

            notification_type = 'approval'
        elif action == 'reject':
            report.status = 'rejected'
            report.review_time = datetime.now()
            report.review_result = reason or '数据异常，需要修改'
            notification_type = 'alert'
        else:
            return {'success': False, 'message': '无效的操作'}

        # 通知企业
        notification = self.notification_agent.generate_notification(
            notification_type, 'enterprise',
            reason=reason or report.review_result
        )

        return {
            'success': True,
            'report_id': report_id,
            'status': report.status,
            'notification': notification
        }

    def get_dashboard(self, user_id: str) -> Dict:
        """获取用户仪表板"""
        if user_id not in self.users:
            return {'success': False, 'message': '用户不存在'}

        user = self.users[user_id]
        user_reports = [r for r in self.reports.values() if r.company_id == user.company_id]

        dashboard_data = {
            'user': user,
            'reports': user_reports,
            'statistics': {
                'total_reports': len(user_reports),
                'approved_reports': len([r for r in user_reports if r.status == 'approved']),
                'pending_reports': len([r for r in user_reports if r.status == 'submitted'])
            }
        }

        # 如果是管理员，提供分析报告
        if user.role in ['city', 'province']:
            analysis = self.analysis_agent.analyze_trend(self.reports.values())
            dashboard_data['analysis'] = analysis

        return dashboard_data

# 演示系统
def demo_system():
    """演示系统运行"""
    system = DataCollectionSystem()

    # 添加测试用户
    system.add_user(User(
        id='E001',
        name='云南某某科技有限公司',
        role='enterprise',
        company_id='CN123456789',
        region='昆明市'
    ))

    system.add_user(User(
        id='C001',
        name='昆明市人社局',
        role='city',
        region='昆明市'
    ))

    # 模拟数据提交
    print("=" * 50)
    print("演示1: 企业数据提交")
    print("=" * 50)

    # 正常数据提交
    normal_data = {
        'company_id': 'CN123456789',
        'employment_count': 150,
        'change_reason': '业务扩展，新增就业岗位'
    }

    result = system.submit_report('E001', normal_data)
    print(f"提交结果: {result}")

    # 异常数据提交
    abnormal_data = {
        'company_id': 'CN123456789',
        'employment_count': 10000,  # 超出范围
        'change_reason': '正常经营'
    }

    print("\n" + "=" * 50)
    print("演示2: 异常数据处理")
    print("=" * 50)

    result = system.submit_report('E001', abnormal_data)
    print(f"异常数据提交结果: {result}")

    # 模拟审核过程
    print("\n" + "=" * 50)
    print("演示3: 审核流程")
    print("=" * 50)

    # 查找已提交的报告
    submitted_reports = [r for r in system.reports.values() if r.status == 'submitted']
    if submitted_reports:
        report_id = submitted_reports[0].id
        print(f"审核报告: {report_id}")

        # 通过审核
        result = system.review_report('C001', report_id, 'approve')
        print(f"审核结果: {result}")

        # 退回审核
        result = system.review_report('C001', report_id, 'reject', '数据需要核实')
        print(f"退回结果: {result}")

    # 查看仪表板
    print("\n" + "=" * 50)
    print("演示4: 用户仪表板")
    print("=" * 50)

    dashboard = system.get_dashboard('E001')
    print(f"企业仪表板: {dashboard['statistics']}")

    dashboard = system.get_dashboard('C001')
    print(f"管理员仪表板包含分析数据: {'analysis' in dashboard}")

# 运行演示
if __name__ == "__main__":
    print("云南省企业就业失业数据采集系统 - Agent演示")
    print("本系统演示了Agent编程在项目管理中的应用：")
    print("1. 数据采集Agent - 负责数据验证")
    print("2. 审核Agent - 负责异常检测")
    print("3. 分析Agent - 负责趋势分析")
    print("4. 通知Agent - 负责智能通知")
    print("\n")

    demo_system()