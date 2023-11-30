/*Daily - BOM - CoSo*/

/*Overview Completion Ratio - All measures*/

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

DECLARE @MarketTradingValue DECIMAL(30,8) 
SET @MarketTradingValue = (
	SELECT
		CAST(SUM([MATCHVALUE]) AS DECIMAL(30,8)) [TradingValue]
	FROM [Flex_MarketInfo]
	WHERE [TRADEPLACE] IN ('HNX','HOSE')
		AND [TXDATE] = @Date
);

WITH

[BadDebt] AS (
	SELECT [SoTaiKhoan]
	FROM [BadDebtAccounts]
	WHERE MONTH([Ngay]) = MONTH(@Date) - 1
)

, [RRE0386.Flex] AS (
	SELECT
		[AUTOID]
		, MIN([AUTOID]) OVER (PARTITION BY [SoTaiKhoan], [NgayMoTK]) [MinID]
		, [NgayMoTK]
		, [SoTaiKhoan]
		, [IDNhanVienMoTK]
	FROM [RRE0386]
	WHERE [RRE0386].[NgayMoTK] = @Date
		AND [RRE0386].[IDNhanVienHienTai] IS NOT NULL
)

, [FindLastBranchID] AS (
	SELECT DISTINCT
		[relationship].[date]
		, [relationship].[account_code] [SoTaiKhoan]
		, [broker_id]
		, LAST_VALUE([branch_id]) OVER(PARTITION BY [account_code], [broker_id] ORDER BY [account_code]) [branch_id]
	FROM [relationship]
	WHERE [relationship].[date] = @Date
		AND [relationship].[account_code] IN (SELECT [SoTaiKhoan] FROM [RRE0386.Flex])
)

, [Rel] AS (
	SELECT
		[Date]
		, [SoTaiKhoan]
		, CASE
			WHEN [broker_id] IS NULL AND [date] <> @Date THEN LEAD([branch_id]) OVER (PARTITION BY [SoTaiKhoan] ORDER BY [date])
			ELSE [branch_id]
		END [BranchID]
	FROM [FindLastBranchID]
)

, [_RRE0386] AS (
	SELECT
		[NgayMoTK]
		, [SoTaiKhoan]
		, [IDNhanVienMoTK]
	FROM [RRE0386.Flex]
	WHERE [MinID] = [AUTOID]
)

, [TargetOrigin] AS (
	SELECT
		[Year]
		, [BranchID]
		, [Measure]
		, CAST([Target] AS FLOAT) [Target]
	FROM [DWH-AppData].[dbo].[BMD.FlexTarget]
	WHERE [Year] = YEAR(@Date)
)

, [CompanyTarget] AS (
	SELECT
		SUM([Market Share]) [MarketShare]
		, SUM([Fee Income]) / @WorkDaysOfYear [FeeIncome]
		, SUM([Interest Income]) / @WorkDaysOfYear [InterestIncome]
		, CAST(SUM([New Accounts]) / @WorkDaysOfYear AS DECIMAL (20, 3)) [NewAccounts]
	FROM [TargetOrigin]
	PIVOT (
		SUM([Target]) FOR [Measure] IN ([Market Share], [Fee Income], [Interest Income], [New Accounts])
	) [z]
)

, [ActualMarketShare] AS (
	SELECT
		CAST(CAST(SUM([trading_record].[value]) AS DECIMAL(30,8)) / @MarketTradingValue / 2 AS DECIMAL(30,8)) [Actual]
		, MAX([Target].[MarketShare]) [Target]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	CROSS JOIN (SELECT [MarketShare] FROM [CompanyTarget]) [Target]
	WHERE [trading_record].[date] = @Date
		AND [relationship].[branch_id] IN (SELECT DISTINCT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date))
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
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
	WHERE [trading_record].[date] = @Date
		AND [relationship].[branch_id] IN (SELECT DISTINCT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date))
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
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
	WHERE [rln0019].[date] = @Date
		AND [relationship].[branch_id] IN (SELECT DISTINCT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date))
		AND [relationship].[account_code] NOT IN (SELECT [SoTaiKhoan] FROM [BadDebt])
)

, [ActualNewAccounts] AS (
	SELECT
		CAST(COUNT(*) AS DECIMAL(8,2)) [Actual]
		, MAX([Target].[NewAccounts]) [Target]
	FROM [_RRE0386]
	LEFT JOIN [Rel]
		ON [Rel].[SoTaiKhoan] = [_RRE0386].[SoTaiKhoan]
	CROSS JOIN (SELECT [NewAccounts] FROM [CompanyTarget]) [Target]
	WHERE [Rel].[BranchID] IN (SELECT DISTINCT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date))
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
