/*MTD - BOM - PhaiSinh*/

/*Headline Tag - Fee Income (Phần trăm hoàn thành chỉ tiêu tháng - Phí giao dịch) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfMonthOfCurrentYear DATETIME;
SET @FirstDateOfMonthOfCurrentYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),MONTH(@Date),1,0,0,0,0));

DECLARE @DateOfPreviousYear DATETIME;
IF MONTH(@Date) = 2 AND DAY(@Date) = 29
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,2,28,0,0,0,0));
ELSE
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,MONTH(@Date),DAY(@Date),0,0,0,0));

DECLARE @FirstDateOfMonthOfPreviousYear DATETIME;
SET @FirstDateOfMonthOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@DateOfPreviousYear),MONTH(@DateOfPreviousYear),1,0,0,0,0));

WITH

[TargetByBranch] AS (
	SELECT [BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Fee Income'
)

, [Rel] AS (
	SELECT DISTINCT
		[date] [Date]
 		, [branch_id] [BranchID]
		, [broker_id] [BrokerID]
		, [account_code] [AccountCode]
	FROM [relationship]
	WHERE [date] BETWEEN @FirstDateOfMonthOfPreviousYear AND @Date
)

, [PrevValue] AS (
	SELECT
		SUM([RRE0018].[PhiGiaoDichPHSThu]) [FeeIncome]
	FROM [RRE0018]
	LEFT JOIN [Rel]
        ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
	WHERE [RRE0018].[Ngay] BETWEEN @FirstDateOfMonthOfPreviousYear AND @DateOfPreviousYear
		AND [Rel].[BranchID] IN (SELECT [BranchID] FROM [TargetByBranch])
)

, [TodayValue] AS (
	SELECT
		SUM([RRE0018].[PhiGiaoDichPHSThu]) [FeeIncome]
	FROM [RRE0018]
	LEFT JOIN [Rel]
        ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
	WHERE [RRE0018].[Ngay] BETWEEN @FirstDateOfMonthOfCurrentYear AND @Date
		AND [Rel].[BranchID] IN (SELECT [BranchID] FROM [TargetByBranch])
)

SELECT
	[TodayValue].[FeeInCome] [FeeIncome]
	, [TodayValue].[FeeInCome] - [PrevValue].[FeeInCome] [AbsoluteChange]
	, CASE 
		WHEN [PrevValue].[FeeInCome] = 0 THEN 0
		ELSE [TodayValue].[FeeInCome] / [PrevValue].[FeeInCome] - 1
	END [RelativeChange]
FROM [PrevValue]
CROSS JOIN [TodayValue]


END
