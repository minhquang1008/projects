/*Daily - BOM - PhaiSinh*/

/*Overview Completion Ratio - All measures (Phần trăm hoàn thành chỉ tiêu ngày - đồ thị cột có format 4 vòng tròn) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @WorkDaysOfYear INT;
SET @WorkDaysOfYear = (
	SELECT COUNT(*)
	FROM [Date] 
	WHERE [Work] = 1 
		AND YEAR([Date]) = YEAR(@Date)
);

DECLARE @MarketTotalContracts DECIMAL(30,2) 
SET @MarketTotalContracts = (
	SELECT
		SUM(ISNULL([FDS_MarketInfo].[MkTradingVol],0)) [TotalContracts]
	FROM [DWH-CoSo].[dbo].[FDS_MarketInfo]
	WHERE [Txdate] = @Date
);

WITH 

[Rel] AS (
	SELECT DISTINCT
		[branch_id] [BranchID]
		, [broker_id] [BrokerID]
		, [account_code] [AccountCode]
	FROM [relationship]
	WHERE [date] = @Date
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
		, SUM([Fee Income]) / @WorkDaysOfYear [FeeIncome]
	FROM [TargetOrigin]
	PIVOT (
		SUM([Target]) FOR [Measure] IN ([Market Share], [Fee Income])
	) [z]
)

, [ActualMarketShare] AS (
	SELECT
		 CAST(CAST(SUM([RRE0018].[SoLuongHopDong]) AS DECIMAL(30,8)) / @MarketTotalContracts / 2 AS DECIMAL(30,8)) [Actual]
		, MAX([Target].[MarketShare]) [Target]
	FROM [RRE0018]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
	CROSS JOIN (SELECT [MarketShare] FROM [CompanyTarget]) [Target]
	WHERE [RRE0018].[Ngay] = @Date
		AND [Rel].[BranchID] IN (SELECT DISTINCT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date) AND [Measure] = 'Market Share')
)

, [ActualFeeIncome] AS (
	SELECT
		SUM([RRE0018].[PhiGiaoDichPHSThu]) [Actual]
		, MAX([Target].[FeeIncome]) [Target]
	FROM [RRE0018]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
	CROSS JOIN (SELECT [FeeIncome] FROM [CompanyTarget]) [Target]
	WHERE [RRE0018].[Ngay] = @Date
		AND [Rel].[BranchID] IN (SELECT DISTINCT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date) AND [Measure] = 'Fee Income')
)

SELECT
	[ActualMarketShare].[Actual]/[ActualMarketShare].[Target] [MarketShare]
	, [ActualFeeIncome].[Actual]/[ActualFeeIncome].[Target] [FeeIncome]
FROM [ActualMarketShare]
CROSS JOIN [ActualFeeIncome]


END




