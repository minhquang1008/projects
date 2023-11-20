/*MTD - BOM*/

/*Overview Completion Ratio - All measures (Phần trăm hoàn thành chỉ tiêu ngày - đồ thị cột có format 4 vòng tròn) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonth DATETIME;
SET @FirstDateOfMonth = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

DECLARE @MarketTradingValue DECIMAL(30,2)
SET @MarketTradingValue = (
	SELECT
		SUM([TongGiaTriGiaoDich]) [TradingValue]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichCoSoVietStock]
	WHERE [San] IN ('HNX','HOSE')
		AND [Ngay] BETWEEN @FirstDateOfMonth AND @Date
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
		, SUM([Interest Income]) / 12 [InterestIncome]
		, CAST(SUM([New Accounts]) / 12 AS DECIMAL (20, 0)) [NewAccounts]
	FROM [BranchTargetByYear]
	PIVOT (
		SUM([Target]) FOR [Measure] IN ([Market Share], [Fee Income], [Interest Income], [New Accounts])
	) [z]
	WHERE [Year] = YEAR(@Date)
)

, [ActualMarketShare] AS (
	SELECT
		SUM([trading_record].[value]) / @MarketTradingValue / 2 [Actual]
		, MAX([Target].[MarketShare]) [Target]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	CROSS JOIN (SELECT [MarketShare] FROM [CompanyTarget]) [Target]
	WHERE [trading_record].[date] BETWEEN @FirstDateOfMonth AND @Date
		AND [relationship].[branch_id] IN (SELECT DISTINCT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date))
)

, [ActualFeeIncome] AS (
	SELECT
		SUM([trading_record].[fee]) [Actual]
		, MAX([Target].[FeeIncome]) [Target]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	CROSS JOIN (SELECT [FeeIncome] FROM [CompanyTarget]) [Target]
	WHERE [trading_record].[date] BETWEEN @FirstDateOfMonth AND @Date
		AND [relationship].[branch_id] IN (SELECT DISTINCT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date))
)

, [ActualInterestIncome] AS (
	SELECT
		SUM([rln0019].[interest]) [Actual]
		, MAX([Target].[InterestIncome]) [Target]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [rln0019].[sub_account]
		AND [relationship].[date] = [rln0019].[date]
	CROSS JOIN (SELECT [InterestIncome] FROM [CompanyTarget]) [Target]
	WHERE [rln0019].[date] BETWEEN @FirstDateOfMonth AND @Date
		AND [relationship].[branch_id] IN (SELECT DISTINCT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date))
)

, [ActualNewAccounts] AS (
	SELECT
		CAST(COUNT(*) AS DECIMAL(8,2)) [Actual]
		, MAX([Target].[NewAccounts]) [Target]
	FROM [customer_change]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [customer_change].[account_code]
		AND [Rel].[Date] = [customer_change].[open_date]
	CROSS JOIN (SELECT [NewAccounts] FROM [CompanyTarget]) [Target]
	WHERE [Rel].[BranchID] IN (SELECT DISTINCT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date))
		AND [customer_change].[open_date] BETWEEN @FirstDateOfMonth AND @Date
		AND [customer_change].[open_or_close] = 'Mo'
		AND [Rel].[BrokerID] IS NOT NULL -- không tính các tài khoản chưa duyệt nên chưa có môi giới
		AND [customer_change].[open_date] BETWEEN @FirstDateOfMonth AND @Date
)

SELECT
	[ActualMarketShare].[Actual]/[ActualMarketShare].[Target] [MarketShare]
	, [ActualFeeIncome].[Actual]/[ActualFeeIncome].[Target] [FeeIncome]
	, [ActualInterestIncome].[Actual]/[ActualInterestIncome].[Target] [InterestIncome]
	, [ActualNewAccounts].[Actual]/[ActualNewAccounts].[Target] [NewAccounts]
FROM [ActualMarketShare]
CROSS JOIN [ActualFeeIncome]
CROSS JOIN [ActualInterestIncome]
CROSS JOIN [ActualNewAccounts]


END
