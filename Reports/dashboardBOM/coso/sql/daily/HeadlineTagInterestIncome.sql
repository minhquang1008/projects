/*Daily - BOM - CoSo*/

/*Headline Tag - Interest Income*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Prev DATETIME;
SET @Prev = (
	SELECT MIN([Date]) 
	FROM (
		SELECT TOP 2
			[Date]
		FROM [Date]
		WHERE [Work] = 1
			AND [Date] <= @Date
		ORDER BY [Date] DESC
	) [z]
);

WITH

[BadDebt] AS (
	SELECT 
		CONVERT(VARCHAR(7), [Ngay], 126) [Ngay]
		, [SoTaiKhoan]
	FROM [BadDebtAccounts]
	WHERE [Ngay] BETWEEN DATEADD(MONTH, -1, @Prev) AND @Date
		AND [LoaiNo] NOT IN (N'Hết nợ', N'TK đã đóng')
)

, [TargetByBranch] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Interest Income'
)

, [PrevValue] AS (
	SELECT
		 SUM(CASE WHEN [BadDebt].[SoTaiKhoan] IS NULL THEN [rln0019].[interest] ELSE 0 END) [InterestIncome]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [rln0019].[sub_account]
		AND [relationship].[date] = [rln0019].[date]
	LEFT JOIN [BadDebt]
		ON [BadDebt].[SoTaiKhoan] = [relationship].[account_code]
		AND [BadDebt].[Ngay] = CONVERT(VARCHAR(7), DATEADD(MONTH, -1, [rln0019].[date]), 126)
	WHERE [rln0019].[date] = @Prev
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
)

, [TodayValue] AS (
	SELECT
		SUM(CASE WHEN [BadDebt].[SoTaiKhoan] IS NULL THEN [rln0019].[interest] ELSE 0 END) [InterestIncome]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [rln0019].[sub_account]
		AND [relationship].[date] = [rln0019].[date]
	LEFT JOIN [BadDebt]
		ON [BadDebt].[SoTaiKhoan] = [relationship].[account_code]
		AND [BadDebt].[Ngay] = CONVERT(VARCHAR(7), DATEADD(MONTH, -1, [rln0019].[date]), 126)
	WHERE [rln0019].[date] = @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
)

SELECT
	[TodayValue].[InterestIncome] [InterestIncome]
	, [TodayValue].[InterestIncome] - [PrevValue].[InterestIncome] [AbsoluteChange]
	, CASE 
		WHEN [PrevValue].[InterestIncome] = 0 THEN 0
		ELSE [TodayValue].[InterestIncome] / [PrevValue].[InterestIncome] - 1
	END [RelativeChange]
FROM [PrevValue]
CROSS JOIN [TodayValue]


END