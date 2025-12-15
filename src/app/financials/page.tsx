'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Filler } from 'chart.js'
import { Pie, Bar, Line } from 'react-chartjs-2'

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Filler)

const financialData = {
    peer_navigator_income: [360000, 1320000, 2820000, 5080000, 7220000, 8900000, 10660000, 12830000, 15300000, 18070000],
    training_stipends: [95000, 162000, 241000, 333000, 432000, 520000, 610000, 708000, 815000, 668000],
    research_participation: [382150, 843000, 1320000, 1890000, 2560000, 3240000, 4080000, 5120000, 6400000, 6250000],
    gig_marketplace: [481000, 1060000, 2030000, 3220000, 4390000, 5900000, 7520000, 9600000, 12100000, 14120000],
    career_employment: [2107000, 3800000, 5600000, 7500000, 9800000, 12100000, 14800000, 17500000, 20200000, 22500000],
    career_training: [250000, 431000, 589000, 768000, 1030000, 1250000, 1520000, 1820000, 2180000, 2440000],
    direct_income_totals: [3675000, 7616000, 12599000, 18783000, 25503000, 31990000, 39170000, 47250000, 57010000, 64060000],
    indirect_benefits_totals: [3396000, 6072000, 15975000, 26430000, 44000000, 58930000, 73860000, 88790000, 103720000, 158650000],
    total_participant_impact: [7071000, 13688000, 28574000, 45213000, 69503000, 90920000, 113030000, 136040000, 160730000, 222710000],
    active_participants: [2500, 4500, 8500, 13000, 25000, 35000, 45000, 55000, 65000, 75000],
    impact_per_participant: [2829, 3042, 3361, 3478, 2780, 2598, 2512, 2473, 2472, 2970],
    operating_budget: [3054500, 5200000, 7850000, 11200000, 15500000, 19200000, 22800000, 26500000, 30200000, 34500000],
    cost_per_participant: [1222, 1156, 923, 862, 620, 549, 507, 482, 465, 460],
    funding_core: [1225000, 1900000, 3150000, 4800000, 6300000, 7920000, 9360000, 11000000, 12500000, 14000000],
    funding_workforce: [500000, 800000, 1500000, 2400000, 2500000, 3200000, 4000000, 4800000, 5500000, 4000000],
    funding_research: [300000, 550000, 800000, 1200000, 1500000, 1850000, 2300000, 2800000, 3200000, 3000000],
    funding_csr: [625000, 1000000, 1750000, 2600000, 3000000, 3600000, 4300000, 5000000, 5500000, 5000000],
    funding_foundation: [400000, 700000, 1000000, 1500000, 1500000, 1900000, 2300000, 2700000, 3000000, 3500000],
    funding_commercial: [0, 50000, 0, 500000, 1000000, 730000, 1640000, 1200000, 1500000, 6000000],
    funding_totals: [3050000, 5000000, 8200000, 12100000, 15800000, 19800000, 23900000, 27500000, 31200000, 36500000],
    roi_percent_trend: [131.6, 163.2, 264.1, 303.1, 348.4, 373.0, 395.9, 412.9, 431.8, 545.7],
    per_dollar_invested: [2.32, 2.63, 3.64, 4.03, 4.48, 4.73, 4.96, 5.13, 5.32, 6.46],
    sensitivity_conservative_benefit: [4949700, 9581600, 20001800, 31649100, 48651900, 63644000, 79121000, 95228000, 112511000, 155897000],
    sensitivity_conservative_roi: [62.1, 84.4, 155.3, 182.2, 214.0, 231.1, 247.1, 259.8, 272.6, 352.5],
    sensitivity_aggressive_benefit: [8131650, 15741200, 32860100, 52045000, 79978450, 104558000, 130034500, 156446000, 184840500, 256317000],
    sensitivity_aggressive_roi: [166.2, 203.2, 318.5, 364.3, 415.7, 444.5, 470.2, 489.6, 511.4, 643.2]
}

const incomeStreams = [
    { name: 'Peer Navigator', participants: [120, 220, 470, 800, 1200, 1400, 1700, 2000, 2400, 2800] },
    { name: 'Training Stipends', participants: [190, 270, 362, 480, 600, 720, 850, 1000, 1150, 920] },
    { name: 'Research Participation', participants: [250, 450, 600, 800, 1000, 1200, 1500, 1800, 2200, 2000] },
    { name: 'Gig Tasks/Marketplace', participants: [370, 530, 870, 1300, 1700, 2200, 2600, 3200, 3900, 4400] },
    { name: 'Career Employment', participants: [290, 450, 650, 850, 1100, 1350, 1600, 1900, 2200, 2400] },
    { name: 'Career Training', participants: [500, 862, 1178, 1536, 1800, 2000, 2400, 2800, 3200, 3500] }
]

export default function FinancialDashboard() {
    const [currentYear, setCurrentYear] = useState(0)

    const formatCurrency = (value: number, compact = false) => {
        if (compact && value >= 1000) {
            return '$' + (value / 1000).toFixed(0) + 'K'
        }
        return '$' + value.toLocaleString('en-US', { maximumFractionDigits: 0 })
    }

    const formatNumber = (value: number) => {
        return value.toLocaleString('en-US')
    }

    const copyTable = async (tableId: string) => {
        const table = document.getElementById(tableId)
        if (!table) return

        let text = ''
        table.querySelectorAll('tr').forEach(row => {
            const cells = row.querySelectorAll('th, td')
            const rowText = Array.from(cells).map(cell => (cell as HTMLElement).textContent?.trim()).join('\t')
            text += rowText + '\n'
        })

        await navigator.clipboard.writeText(text)
    }

    const costPieData = {
        labels: ['Personnel (48%)', 'Technology (16%)', 'Support Services (25%)', 'Partnerships (6%)', 'Administration (5%)'],
        datasets: [{
            data: [48, 16, 25, 6, 5],
            backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F']
        }]
    }

    const fundingChartData = {
        labels: ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5', 'Year 6', 'Year 7', 'Year 8', 'Year 9', 'Year 10'],
        datasets: [
            { label: 'IHEP Core', data: financialData.funding_core, backgroundColor: '#1FB8CD' },
            { label: 'Workforce Grants', data: financialData.funding_workforce, backgroundColor: '#FFC185' },
            { label: 'Research Grants', data: financialData.funding_research, backgroundColor: '#B4413C' },
            { label: 'CSR Partnerships', data: financialData.funding_csr, backgroundColor: '#ECEBD5' },
            { label: 'Foundation', data: financialData.funding_foundation, backgroundColor: '#5D878F' },
            { label: 'Commercial', data: financialData.funding_commercial, backgroundColor: '#DB4545' }
        ]
    }

    const roiChartData = {
        labels: ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5', 'Year 6', 'Year 7', 'Year 8', 'Year 9', 'Year 10'],
        datasets: [{
            label: 'ROI %',
            data: financialData.roi_percent_trend,
            borderColor: '#1FB8CD',
            backgroundColor: 'rgba(31, 184, 205, 0.1)',
            fill: true,
            tension: 0.4
        }]
    }

    return (
        <div className="min-h-screen bg-background p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2">IHEP Financial Dashboard</h1>
                    <p className="text-muted-foreground text-lg mb-6">
                        Comprehensive Financial Impact Analysis & Investment Overview
                    </p>

                    <div className="flex items-center gap-3">
                        <label htmlFor="yearSelect" className="font-medium">Select Year:</label>
                        <Select value={currentYear.toString()} onValueChange={(v) => setCurrentYear(parseInt(v))}>
                            <SelectTrigger className="w-[180px]">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                {Array.from({ length: 10 }, (_, i) => (
                                    <SelectItem key={i} value={i.toString()}>Year {i + 1}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                </div>

                {/* Tabs Navigation */}
                <Tabs defaultValue="overview" className="space-y-6">
                    <TabsList className="grid w-full grid-cols-7">
                        <TabsTrigger value="overview">Overview</TabsTrigger>
                        <TabsTrigger value="income">Income Streams</TabsTrigger>
                        <TabsTrigger value="impact">Financial Impact</TabsTrigger>
                        <TabsTrigger value="costs">Operating Costs</TabsTrigger>
                        <TabsTrigger value="funding">Funding Model</TabsTrigger>
                        <TabsTrigger value="roi">ROI Analysis</TabsTrigger>
                        <TabsTrigger value="sensitivity">Sensitivity</TabsTrigger>
                    </TabsList>

                    {/* Overview Tab */}
                    <TabsContent value="overview" className="space-y-6">
                        <h2 className="text-2xl font-bold">Overview Dashboard</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                            <Card className="bg-blue-50 dark:bg-blue-950">
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm text-muted-foreground uppercase">Total Direct Participant Income</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-3xl font-bold">{formatCurrency(financialData.direct_income_totals[currentYear], true)}</div>
                                </CardContent>
                            </Card>

                            <Card className="bg-green-50 dark:bg-green-950">
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm text-muted-foreground uppercase">Total Indirect Benefits</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-3xl font-bold">{formatCurrency(financialData.indirect_benefits_totals[currentYear], true)}</div>
                                </CardContent>
                            </Card>

                            <Card className="bg-purple-50 dark:bg-purple-950">
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm text-muted-foreground uppercase">Total Financial Impact</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-3xl font-bold">{formatCurrency(financialData.total_participant_impact[currentYear], true)}</div>
                                </CardContent>
                            </Card>

                            <Card className="bg-orange-50 dark:bg-orange-950">
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm text-muted-foreground uppercase">Active Participants</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-3xl font-bold">{formatNumber(financialData.active_participants[currentYear])}</div>
                                </CardContent>
                            </Card>

                            <Card className="bg-red-50 dark:bg-red-950">
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm text-muted-foreground uppercase">Cost Per Participant</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-3xl font-bold">{formatCurrency(financialData.cost_per_participant[currentYear])}</div>
                                </CardContent>
                            </Card>
                        </div>
                    </TabsContent>

                    {/* Income Streams Tab */}
                    <TabsContent value="income">
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between">
                                <CardTitle>Participant Income Sources</CardTitle>
                                <Button variant="outline" size="sm" onClick={() => copyTable('incomeTable')}>Copy Table</Button>
                            </CardHeader>
                            <CardContent>
                                <div className="overflow-x-auto">
                                    <table id="incomeTable" className="w-full">
                                        <thead>
                                            <tr className="border-b">
                                                <th className="text-left p-3">Stream Name</th>
                                                <th className="text-right p-3">Participant Count</th>
                                                <th className="text-right p-3">Avg Earnings</th>
                                                <th className="text-right p-3">Total Annual</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {incomeStreams.map((stream, idx) => {
                                                const total = [financialData.peer_navigator_income, financialData.training_stipends, financialData.research_participation, financialData.gig_marketplace, financialData.career_employment, financialData.career_training][idx][currentYear]
                                                const participants = stream.participants[currentYear]
                                                const avg = participants > 0 ? total / participants : 0
                                                return (
                                                    <tr key={idx} className="border-b hover:bg-accent">
                                                        <td className="p-3">{stream.name}</td>
                                                        <td className="text-right p-3">{formatNumber(participants)}</td>
                                                        <td className="text-right p-3">{formatCurrency(avg)}</td>
                                                        <td className="text-right p-3">{formatCurrency(total)}</td>
                                                    </tr>
                                                )
                                            })}
                                        </tbody>
                                        <tfoot>
                                            <tr className="bg-accent font-semibold">
                                                <td className="p-3">TOTAL</td>
                                                <td className="text-right p-3">{formatNumber(incomeStreams.reduce((sum, stream) => sum + stream.participants[currentYear], 0))}</td>
                                                <td className="text-right p-3">—</td>
                                                <td className="text-right p-3">{formatCurrency(financialData.direct_income_totals[currentYear])}</td>
                                            </tr>
                                        </tfoot>
                                    </table>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Financial Impact Tab */}
                    <TabsContent value="impact">
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between">
                                <CardTitle>10-Year Financial Impact Projection</CardTitle>
                                <Button variant="outline" size="sm" onClick={() => copyTable('impactTable')}>Copy Table</Button>
                            </CardHeader>
                            <CardContent>
                                <div className="overflow-x-auto">
                                    <table id="impactTable" className="w-full">
                                        <thead>
                                            <tr className="border-b">
                                                <th className="text-left p-3">Year</th>
                                                <th className="text-right p-3">Direct Income</th>
                                                <th className="text-right p-3">Indirect Benefits</th>
                                                <th className="text-right p-3">Total Impact</th>
                                                <th className="text-right p-3">Active Participants</th>
                                                <th className="text-right p-3">Per Participant</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {Array.from({ length: 10 }, (_, i) => (
                                                <tr key={i} className="border-b hover:bg-accent">
                                                    <td className="p-3">Year {i + 1}</td>
                                                    <td className="text-right p-3">{formatCurrency(financialData.direct_income_totals[i])}</td>
                                                    <td className="text-right p-3">{formatCurrency(financialData.indirect_benefits_totals[i])}</td>
                                                    <td className="text-right p-3">{formatCurrency(financialData.total_participant_impact[i])}</td>
                                                    <td className="text-right p-3">{formatNumber(financialData.active_participants[i])}</td>
                                                    <td className="text-right p-3">{formatCurrency(financialData.impact_per_participant[i])}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Operating Costs Tab */}
                    <TabsContent value="costs" className="space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>Cost Breakdown by Category</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="h-[400px]">
                                    <Pie data={costPieData} options={{ responsive: true, maintainAspectRatio: false }} />
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between">
                                <CardTitle>Operating Budget & Efficiency</CardTitle>
                                <Button variant="outline" size="sm" onClick={() => copyTable('costsTable')}>Copy Table</Button>
                            </CardHeader>
                            <CardContent>
                                <div className="overflow-x-auto">
                                    <table id="costsTable" className="w-full">
                                        <thead>
                                            <tr className="border-b">
                                                <th className="text-left p-3">Year</th>
                                                <th className="text-right p-3">Operating Budget</th>
                                                <th className="text-right p-3">Active Participants</th>
                                                <th className="text-right p-3">Cost Per Participant</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {Array.from({ length: 10 }, (_, i) => (
                                                <tr key={i} className="border-b hover:bg-accent">
                                                    <td className="p-3">Year {i + 1}</td>
                                                    <td className="text-right p-3">{formatCurrency(financialData.operating_budget[i])}</td>
                                                    <td className="text-right p-3">{formatNumber(financialData.active_participants[i])}</td>
                                                    <td className="text-right p-3">{formatCurrency(financialData.cost_per_participant[i])}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Funding Model Tab */}
                    <TabsContent value="funding" className="space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>Funding Sources by Year</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="h-[400px]">
                                    <Bar
                                        data={fundingChartData}
                                        options={{
                                            responsive: true,
                                            maintainAspectRatio: false,
                                            scales: {
                                                x: { stacked: true },
                                                y: {
                                                    stacked: true,
                                                    ticks: {
                                                        callback: (value) => '$' + (Number(value) / 1000000).toFixed(1) + 'M'
                                                    }
                                                }
                                            }
                                        }}
                                    />
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between">
                                <CardTitle>Detailed Funding Breakdown</CardTitle>
                                <Button variant="outline" size="sm" onClick={() => copyTable('fundingTable')}>Copy Table</Button>
                            </CardHeader>
                            <CardContent>
                                <div className="overflow-x-auto">
                                    <table id="fundingTable" className="w-full">
                                        <thead>
                                            <tr className="border-b">
                                                <th className="text-left p-3">Year</th>
                                                <th className="text-right p-3">IHEP Core</th>
                                                <th className="text-right p-3">Grants</th>
                                                <th className="text-right p-3">Research</th>
                                                <th className="text-right p-3">CSR</th>
                                                <th className="text-right p-3">Foundation</th>
                                                <th className="text-right p-3">Commercial</th>
                                                <th className="text-right p-3">Total</th>
                                                <th className="text-right p-3">Surplus/Deficit</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {Array.from({ length: 10 }, (_, i) => {
                                                const surplus = financialData.funding_totals[i] - financialData.operating_budget[i]
                                                return (
                                                    <tr key={i} className="border-b hover:bg-accent">
                                                        <td className="p-3">Year {i + 1}</td>
                                                        <td className="text-right p-3">{formatCurrency(financialData.funding_core[i])}</td>
                                                        <td className="text-right p-3">{formatCurrency(financialData.funding_workforce[i])}</td>
                                                        <td className="text-right p-3">{formatCurrency(financialData.funding_research[i])}</td>
                                                        <td className="text-right p-3">{formatCurrency(financialData.funding_csr[i])}</td>
                                                        <td className="text-right p-3">{formatCurrency(financialData.funding_foundation[i])}</td>
                                                        <td className="text-right p-3">{formatCurrency(financialData.funding_commercial[i])}</td>
                                                        <td className="text-right p-3">{formatCurrency(financialData.funding_totals[i])}</td>
                                                        <td className={`text-right p-3 ${surplus >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                            {formatCurrency(surplus)}
                                                        </td>
                                                    </tr>
                                                )
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* ROI Analysis Tab */}
                    <TabsContent value="roi" className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <Card>
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm text-muted-foreground">Cost per Participant</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold">{formatCurrency(financialData.cost_per_participant[currentYear])}</div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm text-muted-foreground">Benefit per Participant</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-green-600">{formatCurrency(financialData.impact_per_participant[currentYear])}</div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm text-muted-foreground">ROI Percentage</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-green-600">{financialData.roi_percent_trend[currentYear].toFixed(1)}%</div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm text-muted-foreground">Return per $1 Invested</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-green-600">${financialData.per_dollar_invested[currentYear].toFixed(2)}</div>
                                </CardContent>
                            </Card>
                        </div>

                        <Card>
                            <CardHeader>
                                <CardTitle>ROI Trend Over 10 Years</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="h-[400px]">
                                    <Line data={roiChartData} options={{ responsive: true, maintainAspectRatio: false }} />
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Sensitivity Analysis Tab */}
                    <TabsContent value="sensitivity">
                        <div className="space-y-4">
                            <p className="text-muted-foreground">Impact projections under different scenarios for the selected year</p>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <Card>
                                    <CardHeader>
                                        <CardTitle>Conservative Scenario (70%)</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <div>
                                            <div className="text-sm text-muted-foreground">Total Benefit</div>
                                            <div className="text-xl font-bold">{formatCurrency(financialData.sensitivity_conservative_benefit[currentYear])}</div>
                                        </div>
                                        <div>
                                            <div className="text-sm text-muted-foreground">ROI Percentage</div>
                                            <div className="text-xl font-bold text-green-600">{financialData.sensitivity_conservative_roi[currentYear].toFixed(1)}%</div>
                                        </div>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader>
                                        <CardTitle>Base Case (100%)</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <div>
                                            <div className="text-sm text-muted-foreground">Total Benefit</div>
                                            <div className="text-xl font-bold">{formatCurrency(financialData.total_participant_impact[currentYear])}</div>
                                        </div>
                                        <div>
                                            <div className="text-sm text-muted-foreground">ROI Percentage</div>
                                            <div className="text-xl font-bold text-green-600">{financialData.roi_percent_trend[currentYear].toFixed(1)}%</div>
                                        </div>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader>
                                        <CardTitle>Aggressive Scenario (115%)</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <div>
                                            <div className="text-sm text-muted-foreground">Total Benefit</div>
                                            <div className="text-xl font-bold">{formatCurrency(financialData.sensitivity_aggressive_benefit[currentYear])}</div>
                                        </div>
                                        <div>
                                            <div className="text-sm text-muted-foreground">ROI Percentage</div>
                                            <div className="text-xl font-bold text-green-600">{financialData.sensitivity_aggressive_roi[currentYear].toFixed(1)}%</div>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>
                        </div>
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    )
}
