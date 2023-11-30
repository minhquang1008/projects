/*YTD - BOM - CoSo*/

/*Trailing - Interest Income (So sánh 5 năm gần nhất)*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATETIMEFROMPARTS(YEAR(@Date)-4,1,1,0,0,0,0);

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

, [YearlyTarget] AS (
    SELECT 
		[Year]
        , SUM(CAST([Target] AS FLOAT)) [Target]
	FROM [DWH-AppData].[dbo].[BMD.FlexTarget]
	WHERE [Year] BETWEEN YEAR(@Since) AND YEAR(@Date)
        AND [Measure] = 'Interest Income'
	GROUP BY [Year]
)

, [ValueAllBranchesByDate] AS (
	SELECT
		DATETIMEFROMPARTS(YEAR([rln0019].[date]),12,31,0,0,0,0) [Date]
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
	GROUP BY DATETIMEFROMPARTS(YEAR([rln0019].[date]),12,31,0,0,0,0)
)

SELECT
	[ValueAllBranchesByDate].[Date]
	, [ValueAllBranchesByDate].[Actual]
	, [YearlyTarget].[Target]
FROM [YearlyTarget]
LEFT JOIN [ValueAllBranchesByDate]
	ON YEAR([ValueAllBranchesByDate].[Date]) = [YearlyTarget].[Year]
ORDER BY 1


END