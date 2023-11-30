/*MTD - BOM - CoSo*/

/*Overview Completion Ratio - All measures*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonth DATETIME;
SET @FirstDateOfMonth = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

DECLARE @MarketTradingValue DECIMAL(30,2)
SET @MarketTradingValue = (
	SELECT
		CAST(SUM([MATCHVALUE]) AS DECIMAL(30,8)) [TradingValue]
	FROM [Flex_MarketInfo]
	WHERE [TRADEPLACE] IN ('HNX','HOSE')
		AND [TXDATE] BETWEEN @FirstDateOfMonth AND @Date
);

WITH 

[BadDebt] AS (
	SELECT 
		CONVERT(VARCHAR(7), [Ngay], 126) [Ngay]
		, [SoTaiKhoan]
	FROM [BadDebtAccounts]
	WHERE [Ngay] BETWEEN DATEADD(MONTH, -1, @FirstDateOfMonth) AND @Date
		AND [LoaiNo] NOT IN (N'Hết nợ', N'TK đã đóng')
)

, [RRE0386.Flex] AS (
	SELECT
		[AUTOID]
		, MIN([AUTOID]) OVER (PARTITION BY [SoTaiKhoan], [NgayMoTK]) [MinID]
		, [NgayMoTK]
		, [SoTaiKhoan]
		, [IDNhanVienMoTK]
	FROM [RRE0386]
	WHERE [RRE0386].[NgayMoTK] BETWEEN @FirstDateOfMonth AND @Date
		AND [RRE0386].[IDNhanVienHienTai] IS NOT NULL
)

, [FindLastBranchID] AS (
	SELECT DISTINCT
		[relationship].[date]
		, [relationship].[account_code] [SoTaiKhoan]
		, [broker_id]
		, LAST_VALUE([branch_id]) OVER(PARTITION BY [account_code], [broker_id] ORDER BY [account_code]) [branch_id]
	FROM [relationship]
	WHERE [relationship].[date] BETWEEN @FirstDateOfMonth AND @Date
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
		, SUM([Fee Income]) / 12 [FeeIncome]
		, SUM([Interest Income]) / 12 [InterestIncome]
		, CAST(SUM([New Accounts]) / 12 AS DECIMAL (20, 0)) [NewAccounts]
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
	WHERE [trading_record].[date] BETWEEN @FirstDateOfMonth AND @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date) AND [Measure] = 'Market Share')
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
	WHERE [trading_record].[date] BETWEEN @FirstDateOfMonth AND @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date) AND [Measure] = 'Fee Income')
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
)

, [ActualInterestIncome] AS (
	SELECT
		SUM(CASE WHEN [BadDebt].[SoTaiKhoan] IS NULL THEN [rln0019].[interest] ELSE 0 END) [Actual]
		, MAX([Target].[InterestIncome]) [Target]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [rln0019].[sub_account]
		AND [relationship].[date] = [rln0019].[date]
	LEFT JOIN [BadDebt]
		ON [BadDebt].[SoTaiKhoan] = [relationship].[account_code]
		AND [BadDebt].[Ngay] = CONVERT(VARCHAR(7), DATEADD(MONTH, -1, [rln0019].[date]), 126)
	CROSS JOIN (SELECT [InterestIncome] FROM [CompanyTarget]) [Target]
	WHERE [rln0019].[date] BETWEEN @FirstDateOfMonth AND @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date) AND [Measure] = 'Interest Income')
)

, [ActualNewAccounts] AS (
	SELECT
		CAST(COUNT(*) AS DECIMAL(8,2)) [Actual]
		, MAX([Target].[NewAccounts]) [Target]
	FROM [_RRE0386]
	LEFT JOIN [Rel]
		ON [Rel].[SoTaiKhoan] = [_RRE0386].[SoTaiKhoan]
		AND [Rel].[Date] = [_RRE0386].[NgayMoTK]
	CROSS JOIN (SELECT [NewAccounts] FROM [CompanyTarget]) [Target]
	WHERE [Rel].[BranchID] IN (SELECT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date) AND [Measure] = 'New Accounts')
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
