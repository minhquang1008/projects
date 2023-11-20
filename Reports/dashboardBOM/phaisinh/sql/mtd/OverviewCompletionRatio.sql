/*MTD - BOM - PhaiSinh*/

/*Overview Completion Ratio - All measures (Phần trăm hoàn thành chỉ tiêu tháng - đồ thị cột có format 4 vòng tròn)*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonth DATETIME;
SET @FirstDateOfMonth = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

DECLARE @MarketTotalContracts DECIMAL(30,2) 
SET @MarketTotalContracts = (
	SELECT
		SUM(ISNULL([KhoiLuongKhopLenh],0) + ISNULL([KhoiLuongThoaThuan],0)) [TotalContracts]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichPhaiSinhVietStock]
	WHERE [Ngay] BETWEEN @FirstDateOfMonth AND @Date
);

WITH 

[Rel] AS (
	SELECT DISTINCT
		[date] [Date]
 		, [branch_id] [BranchID]
		, [broker_id] [BrokerID]
		, [account_code] [AccountCode]
	FROM [relationship]
    WHERE [date] BETWEEN @FirstDateOfMonth AND @Date
)

, [CompanyTarget] AS (
	SELECT
		SUM([Market Share]) [MarketShare]
		, SUM([Fee Income]) / 12 [FeeIncome]
	FROM [BranchTargetByYear]
	PIVOT (
		SUM([Target]) FOR [Measure] IN ([Market Share], [Fee Income])
	) [z]
	WHERE [Year] = YEAR(@Date)
)

, [ActualMarketShare] AS (
	SELECT
		SUM([RRE0018].[SoLuongHopDong]) / @MarketTotalContracts / 2 [Actual]
		, MAX([Target].[MarketShare]) [Target]
	FROM [RRE0018]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
	CROSS JOIN (SELECT [MarketShare] FROM [CompanyTarget]) [Target]
	WHERE [RRE0018].[Ngay] BETWEEN @FirstDateOfMonth AND @Date
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
	WHERE [RRE0018].[Ngay] BETWEEN @FirstDateOfMonth AND @Date
		AND [Rel].[BranchID] IN (SELECT DISTINCT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date) AND [Measure] = 'Fee Income')
)

SELECT
	[ActualMarketShare].[Actual]/[ActualMarketShare].[Target] [MarketShare]
	, [ActualFeeIncome].[Actual]/[ActualFeeIncome].[Target] [FeeIncome]
FROM [ActualMarketShare]
CROSS JOIN [ActualFeeIncome]


END




