/*YTD*/

/* Headline Tag - Fee Income (Phần trăm hoàn thành chỉ tiêu tháng - Phí giao dịch) */

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
		AND [Measure] = 'Fee Income'
)

, [ValueByBranchOfPreviousPeriod] AS (
	SELECT
		[relationship].[branch_id] [BranchID]
		, SUM([trading_record].[fee]) [FeeIncome]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] BETWEEN @FirstDateOfPreviousYear AND @DateOfPreviousYear
	GROUP BY [relationship].[branch_id]
)

, [ValueByBranchOfCurrentPeriod] AS (
	SELECT
		[relationship].[branch_id] [BranchID]
		, SUM([trading_record].[fee]) [FeeIncome]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] BETWEEN @FirstDateOfCurrentYear AND @Date
	GROUP BY [relationship].[branch_id]
)

, [result] AS (
	SELECT
		[BranchTarget].[BranchID]
		, ISNULL([ValueByBranchOfCurrentPeriod].[FeeInCome],0) [FeeIncome]
		, ISNULL([ValueByBranchOfCurrentPeriod].[FeeInCome],0) - ISNULL([ValueByBranchOfPreviousPeriod].[FeeInCome],0) [AbsoluteChange]
		, CASE 
			WHEN ISNULL([ValueByBranchOfPreviousPeriod].[FeeInCome],0) = 0 THEN 0
			ELSE ISNULL([ValueByBranchOfCurrentPeriod].[FeeInCome],0) / [ValueByBranchOfPreviousPeriod].[FeeInCome] - 1
		END [RelativeChange]
	FROM [BranchTarget]
	LEFT JOIN [ValueByBranchOfPreviousPeriod]
		ON [BranchTarget].[BranchID] = [ValueByBranchOfPreviousPeriod].[BranchID]
	LEFT JOIN [ValueByBranchOfCurrentPeriod]
		ON [BranchTarget].[BranchID] = [ValueByBranchOfCurrentPeriod].[BranchID]
)

SELECT
	SUM([FeeIncome]) [FeeIncome]
	, SUM([AbsoluteChange]) [AbsoluteChange]
	, SUM([RelativeChange]) [RelativeChange]
FROM [result]


END
