/*MTD - BOM - CoSo*/

/*Fluctuation - Interest Income (Biến động lãi vay ký quỹ)*/

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

, [TargetByBranch] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Interest Income'
)

, [WorkDays] AS (
	SELECT
		[Date]
		, CASE 
			WHEN ISDATE(CONCAT(YEAR([Date]),'-',MONTH([Date]),'-',DAY(@Date))) = 1 
				THEN DATETIMEFROMPARTS(YEAR([Date]),MONTH([Date]),DAY(@Date),0,0,0,0)
			ELSE EOMONTH(DATETIMEFROMPARTS(YEAR([Date]),MONTH([Date]),1,0,0,0,0)) 
		END [EndOfPeriod]
	FROM [Date]
	WHERE
		[Date] BETWEEN @Since AND @Date
		-- AND [Work] = 1
		AND DAY([Date]) <= DAY(@Date)
)

, [Index] AS (
	SELECT 
		[WorkDays].[Date]
		, [WorkDays].[EndOfPeriod]
		, [TargetByBranch].[BranchID]
	FROM [TargetByBranch] CROSS JOIN [WorkDays]
)

, [RawResult] AS (
	SELECT
		[rln0019].[date] [Date]
		, [relationship].[branch_id] [BranchID]
		, SUM(CASE WHEN [BadDebt].[SoTaiKhoan] IS NULL THEN [rln0019].[interest] ELSE 0 END) [InterestIncome]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [relationship].[date] = [rln0019].[Date]
		AND [rln0019].[sub_account] = [relationship].[sub_account]
	LEFT JOIN [BadDebt]
		ON [BadDebt].[SoTaiKhoan] = [relationship].[account_code]
		AND [BadDebt].[Ngay] = CONVERT(VARCHAR(7), DATEADD(MONTH, -1, [rln0019].[date]), 126)
	WHERE [rln0019].[date] BETWEEN @Since AND @Date
	GROUP BY [rln0019].[date], [relationship].[branch_id]
)

SELECT
	[Index].[EndOfPeriod] [Date]
	, ISNULL(SUM([RawResult].[InterestIncome]), 0) [Value]
FROM [Index]
LEFT JOIN [RawResult]
	ON [RawResult].[Date] = [Index].[Date]
	AND [RawResult].[BranchID] = [Index].[BranchID]
GROUP BY [Index].[EndOfPeriod]
ORDER BY [Index].[EndOfPeriod]


END
