/*YTD*/

/* Headline Tag - Interest Income (Phần trăm hoàn thành chỉ tiêu ngày - Lãi vay ký quỹ) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfCurrentYear DATETIME;
SET @FirstDateOfCurrentYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

DECLARE @DateOfPreviousYear DATETIME;
IF MONTH(@Date) = 2 AND DAY(@Date) = 29
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,2,28,0,0,0,0));
ELSE
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,MONTH(@Date),DAY(@Date),0,0,0,0));

DECLARE @FirstDateOfPreviousYear DATETIME;
SET @FirstDateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@DateOfPreviousYear),1,1,0,0,0,0));

WITH 

[BranchTarget] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Interest Income'
)

, [ValueByBranchOfPreviousPeriod] AS (
	SELECT
		[relationship].[branch_id] [BranchID],
		SUM([rln0019].[interest]) [InterestIncome]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [rln0019].[sub_account]
		AND [relationship].[date] = [rln0019].[date]
	WHERE [rln0019].[date] BETWEEN @FirstDateOfPreviousYear AND @DateOfPreviousYear
	GROUP BY [relationship].[branch_id]
)

, [ValueByBranchOfCurrentPeriod] AS (
	SELECT
		[relationship].[branch_id] [BranchID],
		SUM([rln0019].[interest]) [InterestIncome]
	FROM [rln0019]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [rln0019].[sub_account]
		AND [relationship].[date] = [rln0019].[date]
	WHERE [rln0019].[date] BETWEEN @FirstDateOfCurrentYear AND @Date
	GROUP BY [relationship].[branch_id]
)

, [result] AS (
	SELECT
		[BranchTarget].[BranchID]
		, ISNULL([ValueByBranchOfCurrentPeriod].[InterestIncome],0) [InterestIncome]
		, ISNULL([ValueByBranchOfCurrentPeriod].[InterestIncome],0) - ISNULL([ValueByBranchOfPreviousPeriod].[InterestIncome],0) [AbsoluteChange]
		, CASE 
			WHEN ISNULL([ValueByBranchOfPreviousPeriod].[InterestIncome],0) = 0 THEN 0
			ELSE ISNULL([ValueByBranchOfCurrentPeriod].[InterestIncome],0) / [ValueByBranchOfPreviousPeriod].[InterestIncome] - 1
		END [RelativeChange]
	FROM [BranchTarget]
	LEFT JOIN [ValueByBranchOfPreviousPeriod]
		ON [BranchTarget].[BranchID] = [ValueByBranchOfPreviousPeriod].[BranchID]
	LEFT JOIN [ValueByBranchOfCurrentPeriod]
		ON [BranchTarget].[BranchID] = [ValueByBranchOfCurrentPeriod].[BranchID]
)

SELECT
	SUM([InterestIncome]) [InterestIncome],
	SUM([AbsoluteChange]) [AbsoluteChange],
	SUM([RelativeChange]) [RelativeChange]
FROM [result]


END