/*MTD - BOM - CoSo*/

/*Trailing - Interest Income*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATEADD(DAY,1,EOMONTH(DATEADD(YEAR,-1,@Date)));

WITH 

[BadDebt] AS (
	SELECT 
		CONVERT(VARCHAR(7), [Ngay], 126) [Ngay]
		, [SoTaiKhoan]
	FROM [BadDebtAccounts]
	WHERE [Ngay] BETWEEN DATEADD(MONTH, -1, @Since) AND @Date
		AND [LoaiNo] NOT IN (N'Hết nợ', N'TK đã đóng')
)

, [BranchList] AS (
	SELECT [BranchID]
	FROM [BranchTargetByYear] 
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Interest Income'
)

, [MonthlyTarget] AS (
	SELECT 
		[Year]
        , CAST(SUM(CAST([Target] AS FLOAT)) / 12 AS DECIMAL(30,8)) [Target]
	FROM [DWH-AppData].[dbo].[BMD.FlexTarget]
	WHERE [Year] IN (YEAR(@Since), YEAR(@Date))
        AND [Measure] = 'Interest Income'
	GROUP BY [Year]
)

, [ValueAllBranchesByDate] AS (
	SELECT
		EOMONTH([rln0019].[date]) [Date]
		, SUM(CASE WHEN [BadDebt].[SoTaiKhoan] IS NULL THEN [rln0019].[interest] ELSE 0 END) [Actual]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [relationship].[date] = [rln0019].[date]
		AND [relationship].[sub_account] = [rln0019].[sub_account]
	LEFT JOIN [BadDebt]
		ON [BadDebt].[SoTaiKhoan] = [relationship].[account_code]
		AND [BadDebt].[Ngay] = CONVERT(VARCHAR(7), DATEADD(MONTH, -1, [rln0019].[date]), 126)
	WHERE [rln0019].[date] BETWEEN @Since AND @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [BranchList])
	GROUP BY EOMONTH([rln0019].[date])
)

SELECT
	[ValueAllBranchesByDate].[Date]
	, [ValueAllBranchesByDate].[Actual]
	, [MonthlyTarget].[Target]
FROM [MonthlyTarget]
LEFT JOIN [ValueAllBranchesByDate]
	ON YEAR([ValueAllBranchesByDate].[Date]) = [MonthlyTarget].[Year]
ORDER BY 1


END