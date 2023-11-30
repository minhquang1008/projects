/*YTD - BOM - PhaiSinh*/

/*Overview Completion Ratio - All measures (Phần trăm hoàn thành chỉ tiêu tháng - đồ thị cột có format 4 vòng tròn) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfYear DATETIME;
SET @FirstDateOfYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

DECLARE @MarketTotalContracts DECIMAL(30,2) 
SET @MarketTotalContracts = (
	SELECT
		SUM(ISNULL([FDS_MarketInfo].[MkTradingVol],0)) [TotalContracts]
	FROM [DWH-CoSo].[dbo].[FDS_MarketInfo]
	WHERE [Txdate] BETWEEN @FirstDateOfYear AND @Date
);

WITH 

[Rel] AS (
	SELECT DISTINCT
		[date] [Date]
 		, [branch_id] [BranchID]
		, [broker_id] [BrokerID]
		, [account_code] [AccountCode]
	FROM [relationship]
	WHERE [date] BETWEEN @FirstDateOfYear AND @Date
)

, [TargetOrigin] AS (
	SELECT
		[Year]
		, [BranchID]
		, [Measure]
		, CAST([Target] AS FLOAT) [Target]
	FROM [DWH-AppData].[dbo].[BMD.FDSTarget]
	WHERE [Year] = YEAR(@Date)
)

, [CompanyTarget] AS (
	SELECT
		SUM([Market Share]) [MarketShare]
		, SUM([Fee Income]) [FeeIncome]
	FROM [TargetOrigin]
	PIVOT (
		SUM([Target]) FOR [Measure] IN ([Market Share], [Fee Income])
	) [z]
	WHERE [Year] = YEAR(@Date)
)

, [ActualMarketShare] AS (
	SELECT
		CAST(CAST(SUM([RRE0018].[SoLuongHopDong]) AS DECIMAL(30,8)) / @MarketTotalContracts / 2 AS DECIMAL(30,8)) [Actual]
		, MAX([Target].[MarketShare]) [Target]
	FROM [RRE0018]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
	CROSS JOIN (SELECT [MarketShare] FROM [CompanyTarget]) [Target]
	WHERE [RRE0018].[Ngay] BETWEEN @FirstDateOfYear AND @Date
		AND [Rel].[BranchID] IN (SELECT DISTINCT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date) AND [Measure] = 'Market Share')
)

, [ActualFeeIncome] AS (
	SELECT
		SUM([RRE0018].[PhiGiaoDichPHSThu]) [Actual]
		, MAX([Target].[FeeIncome]) [Target]
	FROM [RRE0018]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
	CROSS JOIN (SELECT [FeeIncome] FROM [CompanyTarget]) [Target]
	WHERE [RRE0018].[Ngay] BETWEEN @FirstDateOfYear AND @Date
		AND [Rel].[BranchID] IN (SELECT DISTINCT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date) AND [Measure] = 'Fee Income')
)

SELECT
	[ActualMarketShare].[Actual]/[ActualMarketShare].[Target] [MarketShare]
	, [ActualFeeIncome].[Actual]/[ActualFeeIncome].[Target] [FeeIncome]
FROM [ActualMarketShare]
CROSS JOIN [ActualFeeIncome]


END




